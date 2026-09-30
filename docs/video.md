# Prototype Video — Flow, Script & Production Guide (MHTECHIN Innovation Challenge 2026)

Last updated: 2026-09-30

---

## 1. What the judges asked for (decoded)

The Unstop brief prescribes the order; follow it exactly — judges score against it:

1. **Energetic hook** — the core problem, grab attention.
2. **Strategic context** — innovations stall without tech expertise, cloud infra and deployment support → **MHTECHIN is the bridge to market**.
3. **Innovation breakdown** — problem, target users, existing limitations, our solution, unique value.
4. **Tech stack** — high level: AI/GenAI, ML, APIs, cloud, databases (mirror MHTECHIN's enterprise capabilities).
5. **Live demo (centerpiece)** — user entry → real-time AI processing → generated outputs → admin dashboard.

Evaluation criteria to hit visibly: Innovation, Problem relevance, Technical excellence, Solution design, UX, **Scalability**, Feasibility, **Business potential**, **Social impact**, Presentation, **Team collaboration**. The script below tags each section with the criteria it earns.

## 2. Decision: slides first or demo first?

**Slides → Demo → short slides close.** ("Sandwich" structure.)

Reasoning:
- The brief places the demo *after* context, breakdown and tech stack; the demo only lands if viewers already know what MoE, RAG and the 3 zones are.
- But the demo must be the **longest** single block (~40% of runtime) — so keep slides tight.
- Ending on 2 slides (impact/business + MHTECHIN roadmap) lets you close on the pitch, not on a UI screen.
- Exception: open with a **5-second teaser clip** of the app giving a Hindi voice diagnosis *inside* the hook. It proves "this is real" before any slide appears.

**Target length: 6–7 minutes** (no limit was stated; judges watch many videos — under 8 min is safe, under 5 min undersells the demo). Face-cam in a small corner bubble during slides; full screen during demo.

## 3. Timeline at a glance

| # | Segment | Time | Visual | Criteria earned |
|---|---|---|---|---|
| 1 | Hook | 0:00–0:25 | Farmer photo/stat + 5 s app teaser | Problem relevance, Presentation |
| 2 | Team intro | 0:25–0:35 | Team slide | Team collaboration |
| 3 | Strategic context & MHTECHIN bridge | 0:35–1:05 | 1 slide | Business potential, Feasibility |
| 4 | Innovation breakdown | 1:05–2:00 | 2 slides | Innovation, Problem relevance, Social impact |
| 5 | Architecture & tech stack | 2:00–2:50 | Architecture diagram + stack slide | Technical excellence, Solution design, Scalability |
| 6 | **Live demo** | 2:50–5:35 | Screen recording | UX, Technical excellence, Feasibility |
| 7 | Results | 5:35–6:00 | Metrics slide | Technical excellence |
| 8 | Impact, business & MHTECHIN roadmap | 6:00–6:40 | 2 slides | Scalability, Business potential, Social impact |
| 9 | Close | 6:40–6:55 | Title slide + links | Presentation |

## 4. Slide deck (11 slides)

1. **Title** — "Agri-Vision: One App for Every Farm Problem" · team name · MHTECHIN Innovation Challenge 2026 · AgriTech / GenAI.
2. **Hook visual** — photo of a farmer with a diseased crop / sick cow + one big statistic. *(Pick a stat you can cite, e.g. published estimates of crop losses to pests & diseases, or the 2022 lumpy skin disease outbreak that killed a large number of cattle in India — verify the exact figure and source before putting it on screen.)*
3. **Team** — names, roles (Vision/MoE, Cloud AI/RAG/LLM, App/UX, Data/Eval).
4. **Why innovations stall → MHTECHIN bridge** — left: "Lab prototype" (models on a laptop, no GPU serving, no deployment). Right: "Market-ready product" (cloud infra, scalable serving, enterprise deployment). Middle arrow: **MHTECHIN**.
5. **The problem & users** — Target: small/marginal farmers, low connectivity, Hindi-first, mixed crop + livestock farms. Existing limits: separate apps for crops and animals, English-only, cloud-only, generic chatbots that hallucinate dosages.
6. **Our solution + USP** — 4 icons: *One app (crop + livestock)* · *Offline-first edge AI* · *Hindi voice in/out* · *Grounded, cited GenAI advice with safety validator*.
7. **Architecture** — `architecture_diagram.png` (3 zones: Edge → Cloud Assist → Private Farm Memory).
8. **Tech stack** — grouped exactly like the brief asks:
   - **AI/ML:** MobileNetV3 fine-tuned experts, learned Mixture-of-Experts gate, ONNX Runtime, multimodal fusion, confidence & safety gate.
   - **Generative AI:** Qwen2.5-1.5B fine-tuned with QLoRA, RAG (sentence-transformers + FAISS, 49-doc curated KB), Gemini fallback, citation validator.
   - **Speech:** AI4Bharat Hindi ASR/TTS.
   - **APIs:** OpenAI-compatible LLM API (Ollama/vLLM), weather context.
   - **Cloud:** Containerised app on Hugging Face Spaces, LLM service over HTTPS, graceful fallback chain.
   - **Database:** SQLite farm memory (→ Postgres in production), FAISS vector index.
9. **Results** — table from [evaluation_results.md](system/evaluation_results.md): crop experts 97.5% / 98.5%; end-to-end crop **94.5%**, livestock **89.5%** with `both` routing (up from 77.3% / 83.6%). Note: "measured on held-out test sets: 5,433 crop / 487 livestock images".
10. **Impact & business model** — Social: faster diagnosis, fewer animal deaths, less pesticide misuse, voice for low-literacy users. Business: B2G (state agri departments, KVKs, dairy cooperatives), B2B (agri-input companies, insurers — farm health records), freemium for farmers. Cost advantage: most cases resolved offline; cloud GPU only for hard cases.
11. **Roadmap with MHTECHIN** — the production table from [improvements.md §6](improvements.md): Android offline app, GPU autoscaled multi-LoRA serving, Postgres, MLOps, WhatsApp/IVR, more languages. End: "Built by us. Scaled with MHTECHIN."

Design: one idea per slide, max ~20 words, large numbers, green/earth palette, same font throughout.

## 5. Full script (spoken lines)

> Speaker tags: **S1** = team leader, **S2** = tech lead, **S3** = demo driver. Switching voices shows team collaboration; if only one person records, keep the same lines. Speak at ~140 words/min.

### 1. Hook (0:00–0:25) — S1
*On screen: slide 2, then 5-second teaser of the app speaking a Hindi diagnosis.*

> "A farmer in a village notices brown spots spreading on her tomato leaves. The same week, her cow develops lumps on its skin. The nearest agronomist is hours away, the nearest vet even further — and the internet is one bar, on a good day. By the time help arrives, the crop is lost and the disease has spread to the herd.
> What if she could just take a photo, speak in Hindi — and get a trusted answer in seconds, even offline?"
> *[teaser clip plays]* "This is Agri-Vision."

### 2. Team (0:25–0:35) — S1
> "We're team ___: [names and one-word roles]. We built Agri-Vision for the MHTECHIN Innovation Challenge 2026, in AgriTech and Generative AI."

### 3. Strategic context (0:35–1:05) — S1
*Slide 4.*
> "Most AI projects for farmers never leave the lab. Models work on a laptop, but reaching millions of farmers needs GPU serving, cloud infrastructure, secure data handling and reliable deployment — things student teams and early startups rarely have.
> That's exactly the gap MHTECHIN bridges. We've built and validated the intelligence; with MHTECHIN's enterprise cloud and deployment expertise, Agri-Vision can go from prototype to a product in farmers' hands."

### 4. Innovation breakdown (1:05–2:00) — S2
*Slides 5 → 6.*
> "Our users are small and marginal farmers who manage both crops *and* livestock. Today they face three barriers. One — fragmentation: separate apps and separate experts for plants and animals. Two — connectivity: cloud-only apps fail exactly where they're needed. Three — language: most tools are English, text-heavy, and generic chatbots can confidently give dangerous advice.
> Agri-Vision is one app for the whole farm. A photo is automatically routed to crop or livestock specialists. Lightweight AI runs directly on the device, so most diagnoses happen offline, instantly. Farmers can speak symptoms in Hindi and hear the answer back. And when the case is uncertain or safety-critical, it escalates to our own fine-tuned language model, grounded in a verified knowledge base, with every piece of advice cited and safety-checked — no invented drug dosages.
> Our USP: offline-first, voice-first, one app — with generative AI that is grounded and accountable."

### 5. Architecture & tech stack (2:00–2:50) — S2
*Slide 7 then slide 8.*
> "The system has three zones. Zone 1, the edge: an image quality check, a domain router, and a learned Mixture-of-Experts gate that picks among fine-tuned MobileNetV3 experts — two for crops, two for livestock — exported to ONNX so they run on low-end hardware. A confidence and safety gate decides if the answer is good enough to give offline.
> If not, Zone 2, cloud assist: personal data is stripped, retrieval-augmented generation pulls cited documents from our curated knowledge base, and our Qwen 2.5 model, fine-tuned with QLoRA, writes a structured advisory. If that service is unreachable, it automatically falls back to Gemini, and then to a safe offline message — the farmer never sees an error.
> Zone 3 is private farm memory: every case is stored locally and fed back as history, so advice improves season over season.
> It's all behind standard OpenAI-compatible APIs and containers — which means it can move onto enterprise cloud infrastructure without rewriting code."

### 6. Live demo (2:50–5:35) — S3 (screen recording; full script in §6 below)

### 7. Results (5:35–6:00) — S2
*Slide 9.*
> "We measured everything on held-out test data. Our individual experts reach about 97 to 98 percent on crops. End-to-end, after we improved routing to consult every expert in a domain, accuracy rose from 77 to 94.5 percent on crops and from 84 to almost 90 percent on livestock, while cutting missed lumpy skin cases from 34 to 6."

### 8. Impact, business, roadmap (6:00–6:40) — S1
*Slides 10 → 11.*
> "The impact: faster diagnosis, fewer livestock deaths, less pesticide misuse, and a private health record for every farm — accessible by voice. The business model: state agriculture departments, KVKs and dairy cooperatives as B2G partners, agri-input companies and insurers as B2B, free core use for farmers. And because most cases resolve offline, cloud cost grows only with the hard cases.
> With MHTECHIN, our next steps are an offline Android app, autoscaling GPU serving for our fine-tuned models, a managed database, MLOps monitoring, and WhatsApp and IVR access in more Indian languages."

### 9. Close (6:40–6:55) — S1
> "Agri-Vision — one app, every farm problem, any connection, in the farmer's own language. Built by us, ready to scale with MHTECHIN. Thank you."
*On screen: title, live URL, GitHub link, team names.*

## 6. Live demo — shot list & narration (2:50–5:35)

Map to the brief: **user entry → real-time AI processing → generated outputs → admin dashboard.**

| Step | Time | Action on screen | Narration (S3) |
|---|---|---|---|
| D1 User entry | 2:50–3:10 | Open live URL. Login / signup tab. Toggle Hindi/English in sidebar. | "This is our deployed app. A farmer signs up once — one login for the whole farm. Everything is bilingual; I'll switch to Hindi." |
| D2 Case 1: crop, offline | 3:10–3:45 | Auto-Detect tab → upload a clear tomato early-blight leaf → result appears fast. Zoom on: domain = crop, expert chosen, confidence, "resolved offline" advisory. | "I upload a leaf photo. The router detects it's a crop, the Mixture-of-Experts picks the right specialist, and in under a second we get Early Blight with high confidence — resolved fully on the edge, no internet needed, with season-aware guidance." |
| D3 Case 2: livestock + Hindi voice, escalation | 3:45–4:40 | Upload a lumpy-skin cow image + Hindi voice note ("गाय को बुखार है और त्वचा पर गांठें हैं"). Show transcript, fusion, safety gate → escalates to cloud. Show generated advisory, **citations**, **backend used = Qwen (fine-tuned)**, validator checks. Play Hindi TTS. | "Now a cow. The farmer describes symptoms in Hindi — our speech model transcribes it and fuses it with the image. Lumpy skin is contagious, so the safety gate escalates it. Our fine-tuned Qwen model, grounded by retrieval, writes a structured advisory. See the citations — every claim traces back to a verified document, and the validator confirms there are no drug dosages. And the farmer can listen to it in Hindi." |
| D4 Resilience (optional, 15 s) | 4:40–4:55 | Pre-recorded clip: LLM tunnel off → same case → caption shows "Gemini fallback". | "If our model server is unreachable, the system falls back automatically — the farmer always gets safe advice." |
| D5 Low-quality image | 4:55–5:10 | Upload a blurry/dark photo → quality check asks to retake. | "Bad photos are caught before they can cause a wrong diagnosis." |
| D6 Dashboard | 5:10–5:35 | Farm History tab: crop and livestock history, past cases. (If metrics tiles were added: total cases, % offline, top disease.) | "This is the farm dashboard — every case is saved as private farm memory, split by crops and livestock. This history is passed back to the AI, so next season's advice knows what happened this season. For extension officers, the same data gives a view of disease trends across farms." |

**Demo assets to prepare (before recording):**
- 3 images from the test split (tomato early blight, lumpy skin cow, one blurry photo), in a folder on the desktop.
- 1 short Hindi audio clip (5–8 s), recorded clean.
- Browser zoom 110–125%, hide bookmarks bar, close notifications, 1920×1080.
- Pre-warm the Space and the LLM tunnel; run each case once before recording (caches models).

**If Qwen is slow on camera:** keep the real wait but **cut/speed up the waiting in editing** with an on-screen label "⏩ cloud advisory generating (~Xs)". Never fake the output — record the real response.

## 7. Recording & editing guide

- **Tool:** OBS Studio (free) — scene 1: slides + webcam bubble; scene 2: full-screen browser. Or record slides in PowerPoint/Google Slides "record" and the demo separately, then join in Clipchamp (built into Windows 11) / DaVinci Resolve.
- **Audio > video quality.** Use a headset/phone mic in a quiet room; normalize audio; no background music under speech (or at −25 dB max).
- **Record in segments** (per section above) — re-do a segment, not the whole video.
- Add **captions** (Clipchamp auto-captions) — helps judges and fits the accessibility story.
- Lower-third labels on demo: "Edge AI · offline", "Cloud GenAI · Qwen + RAG", "Safety validator".
- Export 1080p MP4, check file size limits on Unstop; upload to YouTube (unlisted) / Drive as backup link.

## 8. Final checklist before submitting

- [ ] Video 6–7 min, order matches the brief (hook → context/MHTECHIN → breakdown → stack → demo → close)
- [ ] MHTECHIN named at least 3 times (context, stack/infra, roadmap/close)
- [ ] Demo shows: user entry, real-time processing, generated output, dashboard
- [ ] Every number on screen comes from `evaluation_results.md` (no invented metrics); hook statistic has a source
- [ ] "Fine-tuned Qwen" claimed only if it actually served the demo response (else say "Qwen 2.5 via Ollama" / show fallback honestly)
- [ ] Live URL + GitHub link on the closing slide; README updated
- [ ] All team members appear or are credited
- [ ] Watched once end-to-end with sound, by someone who didn't record it

## 9. Likely Q&A for the online presentation round (prepare 1-line answers)

| Question | Answer direction |
|---|---|
| Why not just use ChatGPT/Gemini? | Offline-first edge AI; own fine-tuned model = cost control & data privacy; RAG + validator prevents hallucinated dosages; Gemini only as fallback. |
| How does it scale? | Edge handles most cases → cloud load ∝ hard cases; stateless containers; OpenAI-compatible LLM API → vLLM autoscaling on GPU. |
| Why 1.5B model? | Cheap to serve (runs on CPU quantised), fine-tuned for one structured task; RAG supplies the knowledge, not model size. |
| Accuracy on real field photos? | PlantVillage is lab-style; next step is field data collection with KVKs + active learning from agronomist feedback. Be honest. |
| Data privacy? | Farm memory stored locally; PII stripped before any cloud call; production adds encryption + consent. |
| Revenue? | B2G extension programs, B2B agri-input/insurance analytics (aggregated, consented), freemium farmers. |
