# Improvements Plan — Qwen Serving & Deployment (MHTECHIN Innovation Challenge 2026)

> Time budget: **1–2 hours**. Everything below is ordered so that stopping at any point still leaves you with a working, demo-able system.
> Last updated: 2026-09-30

---

## 0. TL;DR (read this if you read nothing else)

1. **Do not fight vLLM.** Our client ([local_llm_client.py](../src/zone2_cloud/llm/local_llm_client.py)) already talks to *any* OpenAI-compatible endpoint. Ollama exposes one at `http://localhost:11434/v1`. Switching is **three environment variables, zero code changes**.
2. **For deployment, do not host Qwen on the same box as the app.** Keep the app light (ONNX + Streamlit) and point it at a separate LLM endpoint. The code already falls back Qwen → Gemini → mock → safe fallback, so the app never breaks if the LLM is down.
3. **For the judges / video (today):** teammate runs Ollama + the fine-tuned Qwen GGUF on their laptop → exposed via a free **Cloudflare Quick Tunnel** → the cloud-hosted app calls it. Free, 15 minutes, real fine-tuned model.
4. **For a "stays up" link:** a free **Hugging Face Docker Space** (2 vCPU / 16 GB RAM) running Ollama with the 1.5B Q4 GGUF. Slow (CPU) but free and permanent. The HF "free Inference API" is gone, but **Spaces hosting is still free** — that is the loophole you want.
5. **Turn the constraint into the pitch.** The challenge brief literally asks you to explain how "promising innovations stall without technical expertise, cloud infrastructure, and deployment support, positioning MHTECHIN as the bridge". Our GPU-serving gap *is* that story. Show the prototype deployment + a clear production architecture MHTECHIN would help build (Section 6).

---

## 1. Understanding the problem

| Constraint | Why it hurts | What it means for us |
|---|---|---|
| vLLM fails locally | vLLM needs Linux + CUDA GPU; on Windows / small GPUs it is painful | Use Ollama (llama.cpp under the hood, runs on CPU or any GPU, Windows/Mac/Linux) |
| HF free serverless inference removed for custom models | Can't just call `api-inference.huggingface.co` with our fine-tuned model | Self-host the model somewhere free, or use free credits |
| Qwen2.5-1.5B + LoRA ≈ 3 GB in fp16 | Won't fit Vercel/serverless (~512 MB) or Streamlit Cloud (~1 GB RAM) | Quantise to GGUF Q4_K_M (≈ 1.0 GB), host separately |
| 1–2 hours left | No time for Kubernetes, GPU clusters, CI/CD | Use tunnels + free PaaS; document production design instead of building it |

**Key architectural fact that saves us:** [advisory_service.py](../src/zone2_cloud/advisory_service.py) already has `ADVISORY_BACKEND=local_llm` with automatic fallback to Gemini and then to a safe static advisory. So *any* hosting failure degrades gracefully — say this in the video, it is a real engineering strength (resilience).

---

## 2. Step 1 — Make Qwen work with Ollama (≈ 30–40 min, teammate's machine)

### 2a. Merge the LoRA into the base model (needs Python with `transformers`, `peft`; CPU is fine for 1.5B)

```python
# merge_lora.py  (run once, anywhere with ~8 GB RAM)
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

BASE = "Qwen/Qwen2.5-1.5B-Instruct"
LORA = "models_cache/llm/agrivision-qwen-lora"
OUT  = "models_cache/llm/agrivision-qwen-merged"

tok = AutoTokenizer.from_pretrained(BASE)
model = AutoModelForCausalLM.from_pretrained(BASE, torch_dtype="auto")
model = PeftModel.from_pretrained(model, LORA).merge_and_unload()
model.save_pretrained(OUT, safe_serialization=True)
tok.save_pretrained(OUT)
```

> Why merge instead of Ollama's `ADAPTER` line: Ollama's safetensors-adapter import is only reliable for a few architectures; merging + GGUF always works for Qwen2.

### 2b. Convert to GGUF and quantise

```bash
git clone --depth 1 https://github.com/ggerganov/llama.cpp
pip install -r llama.cpp/requirements.txt
python llama.cpp/convert_hf_to_gguf.py models_cache/llm/agrivision-qwen-merged \
       --outfile agrivision-f16.gguf --outtype f16
# quantise (use a prebuilt llama.cpp release binary on Windows: llama-quantize.exe)
llama-quantize agrivision-f16.gguf agrivision-q4_k_m.gguf Q4_K_M     # ≈ 1.0 GB
```

**Shortcut if time is very short:** skip quantisation and use `--outtype q8_0` directly in the convert step (≈ 1.6 GB, no separate binary needed).

### 2c. Create the Ollama model

`Modelfile`:
```
FROM ./agrivision-q4_k_m.gguf
PARAMETER temperature 0.2
PARAMETER num_ctx 4096
PARAMETER stop <|im_end|>
```
The GGUF carries Qwen's chat template, so no `TEMPLATE` block is needed (this matches how we trained — `apply_chat_template`).

```bash
ollama create agrivision-advisor -f Modelfile
ollama run agrivision-advisor "Say OK"          # smoke test
```

### 2d. Point the app at it (no code change)

`.env`:
```
ADVISORY_BACKEND=local_llm
LOCAL_LLM_URL=http://localhost:11434/v1
LOCAL_LLM_MODEL=agrivision-advisor
LOCAL_LLM_TIMEOUT_S=120
```

Verify with the existing comparator (offline, no paid calls): `python -m training.llm.compare_backends` — or just run one low-confidence image through the Streamlit app and check the "backend used" caption.

### 2e. Plan B if the merge/convert breaks (keep to 10 min max)
Use the **base** model to prove the pipeline: `ollama pull qwen2.5:1.5b-instruct` and set `LOCAL_LLM_MODEL=qwen2.5:1.5b-instruct`. RAG + validator + citations still work; say honestly in the video "fine-tuned adapter trained; serving the quantised build is the next step". Do not claim fine-tuned outputs you didn't serve.

---

## 3. Step 2 — Deploy the app (≈ 20–30 min)

The app is Streamlit + ONNX experts (~35 MB each) + FAISS index. It needs a persistent Python server (Streamlit uses websockets), so **Vercel is the wrong target for this UI** — use one of:

| Option | Free? | RAM | Effort | Verdict |
|---|---|---|---|---|
| **Hugging Face Space (Streamlit / Docker SDK)** | Yes | 16 GB | Low | ✅ **Recommended** — enough RAM for ONNX + sentence-transformers, public URL, looks professional |
| Streamlit Community Cloud | Yes | ~1 GB | Lowest | ⚠️ OK only if the embedding model + ONNX fit; risky |
| Render / Railway free | Limited | 512 MB | Medium | ❌ Too small, sleeps |
| GitHub Codespaces (devcontainer already in repo) | 60 h/month free | 8 GB | Lowest | ✅ Good fallback for *recording the demo*, not a public link |

### HF Space steps
1. Create Space → SDK **Docker** (or Streamlit) → hardware *CPU basic (free)*.
2. Push the repo (or a slim copy). **ONNX models under `models_cache/` are gitignored** — upload them to the Space with `huggingface-cli upload <user>/<space> models_cache/moe models_cache/moe --repo-type=space` (Git LFS handles the 35 MB files), or host them in a HF *model* repo and download at startup.
3. Add **Secrets** in Space settings: `ADVISORY_BACKEND`, `LOCAL_LLM_URL`, `LOCAL_LLM_MODEL`, `GEMINI_API_KEY` (fallback). Never commit `.env`.
4. Minimal `Dockerfile`:

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV HF_HUB_OFFLINE=0 PYTHONUNBUFFERED=1
EXPOSE 7860
CMD ["streamlit", "run", "src/app/streamlit_app.py", "--server.port=7860", "--server.address=0.0.0.0"]
```

> SQLite farm memory on a free Space is **ephemeral** (resets on restart). Fine for a demo; mention "production uses managed Postgres" (Section 6).

---

## 4. Step 3 — Connect the hosted app to Qwen (pick ONE)

### Option A — Laptop Ollama + Cloudflare Quick Tunnel (✅ recommended for demo day, 10 min, free, no account)
```bash
# on the teammate's machine where Ollama runs
cloudflared tunnel --url http://localhost:11434 --http-host-header localhost:11434
# prints https://<random>.trycloudflare.com
```
Set the Space secret `LOCAL_LLM_URL=https://<random>.trycloudflare.com/v1`. The `--http-host-header` flag matters — Ollama rejects unknown Host headers otherwise.
- Pros: real fine-tuned model, GPU/CPU of the laptop, zero cost.
- Cons: link dies when laptop sleeps; URL changes each run → update the secret before recording/presenting. `ngrok http 11434 --host-header=localhost:11434` is equivalent.
- Security: anyone with the URL can use the model. Set `OLLAMA_ORIGINS` narrowly and shut the tunnel after the demo; for anything longer put a bearer check in front (our client already sends `LOCAL_LLM_API_KEY`).

### Option B — Always-on free: Ollama in a second HF Docker Space (≈ 30 min)
```dockerfile
FROM ollama/ollama:latest
COPY agrivision-q4_k_m.gguf Modelfile /models/
ENV OLLAMA_HOST=0.0.0.0:7860
RUN ollama serve & sleep 5 && ollama create agrivision-advisor -f /models/Modelfile
EXPOSE 7860
ENTRYPOINT ["ollama","serve"]
```
(If the build-time `ollama create` fails, move it into a small start script that runs `ollama serve &`, waits, creates, then `wait`s.)
- 1.5B Q4 on 2 free vCPUs ≈ 5–10 tokens/s → a 400–700 token advisory takes **~1–2 min**. Set `LOCAL_LLM_TIMEOUT_S=180`, and consider lowering `max_tokens` in `local_llm_client.py` to ~450.
- Space sleeps after inactivity → hit it once before the presentation.

### Option C — Free GPU for recording only: Kaggle / Colab + Ollama/vLLM + tunnel
Kaggle gives 30 GPU-h/week (T4). vLLM *does* work there with our original command (`vllm serve ... --enable-lora --lora-modules agrivision-advisor=...`), then `cloudflared tunnel --url http://localhost:8000`. Fast, real, but session lasts ≤ 12 h.

### Option D — Serverless GPU with free credits (story for "production", optional)
**Modal** (monthly free credits) runs vLLM with LoRA on a T4/L4 and scales to zero; OpenAI-compatible URL drops straight into `LOCAL_LLM_URL`. ~30–45 min if someone has done Modal before; otherwise leave it as the documented production path.

### What NOT to spend time on
- Groq / OpenRouter / Together free tiers: they host *base* Qwen models, not our fine-tuned one. Usable only as an extra fallback, not as "our model".
- Trying to fit the LLM in Vercel / Streamlit Cloud — physically doesn't fit.
- Rewriting any client code — it is already provider-agnostic.

---

## 5. Recommended 90-minute schedule

| Time | Person A (app/deploy) | Person B (Ollama machine) | Person C (video) |
|---|---|---|---|
| 0:00–0:10 | Create HF Space, add Dockerfile | Merge LoRA (2a) | Build slides from [video.md](video.md) |
| 0:10–0:35 | Upload ONNX models + FAISS, first build | GGUF convert + `ollama create` (2b–2c) | Slides + script rehearsal |
| 0:35–0:50 | Space running with Gemini/mock backend | Local test with `.env` (2d) | Prepare demo images/audio |
| 0:50–1:05 | Set `LOCAL_LLM_URL` secret to tunnel | Start cloudflared tunnel (Option A) | — |
| 1:05–1:20 | End-to-end test on public URL, 3 demo cases | Keep laptop awake, plugged in | Record demo segment |
| 1:20–1:30 | Draw deployment diagram (Section 6) for the video | Tunnel off after recording | Record slides, edit |

**Hard cutoffs:** if 2a–2c isn't working by 0:45 → Plan B (base `qwen2.5:1.5b-instruct`). If the Space isn't building by 1:00 → record the demo from local/Codespaces and show the Space as "deployment in progress" only if it's true.

---

## 6. Cloud architecture to present (prototype today → production with MHTECHIN)

### Today (what is actually running)
```
 Farmer (browser / phone)
        │ HTTPS
        ▼
 ┌─────────────────────────────┐          HTTPS (OpenAI-compatible /v1)
 │ HF Space: Streamlit app     │ ───────────────────────────────┐
 │  Zone 1: ONNX MoE experts   │                                ▼
 │  RAG: FAISS + embeddings    │                 ┌──────────────────────────────┐
 │  Validator, SQLite memory   │                 │ Ollama: Qwen2.5-1.5B + LoRA  │
 └─────────────────────────────┘                 │ (GGUF Q4) via CF tunnel / HF │
        │ fallback if LLM down                   └──────────────────────────────┘
        ▼
  Gemini API  →  safe static advisory
```

### Production (the "MHTECHIN bridge" slide)
| Layer | Prototype | Production (with MHTECHIN) |
|---|---|---|
| Edge | Streamlit web | Android app with on-device ONNX (offline-first), PWA fallback |
| API | Streamlit server | FastAPI gateway, auth, rate limiting, containerised |
| LLM serving | Ollama on laptop / CPU Space | vLLM on autoscaling GPU (e.g. K8s + KEDA, or serverless GPU), multi-LoRA (one adapter per crop/livestock region) |
| Data | SQLite (ephemeral) | Managed Postgres + object storage for images; farm data encrypted, consent-based |
| Knowledge | 49-doc FAISS | Managed vector DB, KB curated with KVKs/ICAR, versioned |
| MLOps | Manual training runs | CI/CD, model registry, drift monitoring, feedback loop from agronomist corrections |
| Observability | Logs | Metrics dashboards, latency/cost per advisory, alerting |
| Channels | Web | WhatsApp / IVR voice in Hindi + regional languages |

Rough cost talking point: a 1.5B Q4 model serves an advisory on CPU for well under ₹0.10; only uncertain / safety-critical cases (~20–30% by our confidence gate) ever reach Zone 2, so cloud cost scales with *hard* cases, not with users. (Label this as an estimate.)

---

## 7. Quick wins beyond deployment (only if time remains, 5–10 min each)

1. **Enable `routing=both`** as the default — our own eval shows crop accuracy 0.773 → **0.945**, livestock 0.836 → **0.895** ([evaluation_results.md](system/evaluation_results.md)). Biggest accuracy gain for the least effort; put the number on a slide.
2. **Show the backend used** in the UI (Qwen / Gemini fallback / offline) — the caption already exists; make sure it's visible in the demo, it proves the resilience design.
3. **"Admin/insights" view** — the brief mentions admin dashboards. The *Farm History* tab is our dashboard; if 15 min are free, add 3 `st.metric` tiles on top (total cases, % resolved offline, top disease this season) from the SQLite data.
4. **README update**: add the live Space URL, the Ollama instructions, and the eval table. Judges click the repo.
5. **Pre-warm** both Spaces 10 min before presenting.

## 8. Honesty checklist (protects you in Q&A)
- Say "fine-tuned Qwen served via Ollama" only if the merged GGUF is what actually answered.
- The Qwen advisory quality eval (Part C) is still pending — present it as "LoRA-trained, evaluation in progress", not with invented numbers.
- The crop baseline row in the eval is not like-for-like yet (see eval doc §3.1) — compare top1 vs `both` routing instead, those are solid.
