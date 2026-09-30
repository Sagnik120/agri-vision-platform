# Agri·Vision — Pitch Deck Brief (for Claude in the browser)

> **Who this is for:** Claude (browser). You will produce **two deliverables** from this file:
> 1. **`AgriVision_Pitch.pptx`**: a 16:9 PowerPoint pitch deck, light theme, following the design system in Part B and the slide specs in Part D.
> 2. **`AgriVision_Pitch_Script.docx`** (or a Google Doc if that's easier): the full speaker script, laid out as in Part F.
>
> Put each slide's script in the PowerPoint **speaker notes** too.
> Read the whole file before starting. **Every number in this file is real (measured). Do not invent statistics, customers, revenue, partners or awards.** Where a line says `[VERIFY]` or `[FILL]`, keep it as a visible placeholder in yellow highlight so the team can fill it in.

---

## Part A: Context you need

### A1. The event
- **MHTECHIN Innovation Challenge 2026**: a national online innovation competition. Domains used: **AgriTech, Generative AI, AI/ML, Cloud, Social Impact**.
- Judging criteria: Innovation & Originality, Problem Relevance, Technical Excellence, Solution Design, User Experience, Scalability, Feasibility, Business Potential, Social Impact, Presentation & Demonstration, Team Collaboration.
- The organiser's required video/pitch structure (follow this order):
  1. Energetic hook on the core problem.
  2. Strategic context: innovations stall without technical expertise, cloud infrastructure and deployment support, so **MHTECHIN is the bridge to market readiness**.
  3. Innovation breakdown: problem, target users, existing limitations, solution, unique value.
  4. Tech stack: AI/GenAI, ML, APIs, cloud, databases (mirror MHTECHIN's enterprise capabilities).
  5. **Live demo (centerpiece)**: user entry → real-time AI processing → generated outputs → admin dashboard.
- **Tone:** a founder pitch to investors and technical partners. It should read as a startup raising its first round, not as a college report. Confident, specific, evidence-backed, formal.

### A2. The product in one line
**Agri·Vision: "One farm. One app."** A farmer photographs a leaf or an animal and gets a specialist-grade diagnosis **on the phone itself, even without internet**, with clear next steps in **Hindi or English**. Hard or dangerous cases escalate to **our own fine-tuned GenAI advisor**, which cites verified sources. The same data powers an **admin portal** that shows outbreaks as they emerge.

### A3. What makes us stand out (use these as the recurring "proof points")
1. **One app for crops AND livestock.** Existing tools are split; mixed farms need both.
2. **Offline-first edge AI.** Fine-tuned MobileNetV3 experts exported to **ONNX** run on low-end devices. Confident cases are answered on-device ("Answered on-device" badge in the app).
3. **Mixture-of-Experts (MoE) architecture:** a domain router plus a learned gate over 4 fine-tuned specialists (row crops, perennial crops, lumpy skin disease, foot-and-mouth disease).
4. **Multimodal fusion:** photo + the farmer's own words (Hindi/English) + animal sensor readings (temperature, activity, feed intake) + season, region and weather.
5. **Confidence & safety gate:** only uncertain, conflicting or **safety-critical** cases go to the cloud, so cloud cost scales with hard cases, not with users.
6. **Grounded GenAI, not a chatbot:** RAG over a curated **49-document agricultural knowledge base** (sentence-transformers embeddings + FAISS). A **Qwen2.5-1.5B model fine-tuned with QLoRA** writes a structured advisory. A **validator** enforces the schema, blocks drug dosages and checks that every citation exists ("Citations verified" badge). **Gemini is only a fallback**, then a safe static message, so the farmer never sees an error.
7. **Explainable:** "Why the AI decided this", other possibilities, evidence agreement, confidence ring, knowledge sources.
8. **Private farm memory:** every check is saved to the farm's history and fed back as citable context, so advice improves season over season. Personal data is stripped before any cloud call.
9. **Outbreak watch for administrators:** an alert fires when the same disease is reported 3+ times in one region in a week. This is where the B2G value comes from.
10. **Bilingual and accessible:** full Hindi UI (Devanagari fonts), Hindi symptom input, a "Listen" (text-to-speech) button, phone-number + OTP login (no email or password), a mobile tab bar with a camera button.
11. **Production-style engineering:** Next.js web app + FastAPI backend, an OpenAI-compatible LLM API (works with Ollama/vLLM/any provider without code changes), a System Health page (LLM reachable, latency, Gemini fallback status, MoE, model files, uptime).

### A4. Measured results (real; from our evaluation report, held-out test sets)
Test sets: **5,433 crop images (29 classes, PlantVillage)** and **487 cattle images** (lumpy skin / foot-and-mouth / healthy).

| What | Result |
|---|---|
| Crop specialist, row crops (21 classes) | **97.4% accuracy**, macro-F1 0.965, ECE 0.004 (well calibrated) |
| Crop specialist, perennial crops (17 classes) | **97.8% accuracy**, macro-F1 0.969 |
| Livestock specialists | **93.6%** (lumpy skin vs healthy), **95.1%** (foot-and-mouth vs healthy) |
| Crop end-to-end, first design (gate picks 1 expert) | 77.3% |
| **Crop end-to-end, improved routing (all domain experts consulted)** | **94.5%**, macro-F1 0.928 |
| Livestock end-to-end, first design | 83.6% |
| **Livestock end-to-end, improved "disease-first" routing** | **89.5%**, macro-F1 0.892 |
| Missed lumpy-skin cases (predicted healthy) | **34 → 6** (82% fewer dangerous misses) |
| **Livestock vs off-the-shelf AI** (CLIP zero-shot, same 487 images, fair comparison) | 53.0% → **89.5%** (**+36.5 points**) |
| Calibration, crop end-to-end (ECE, lower = confidence can be trusted) | 0.136 → **0.037**; when the app says ≥ 90% sure it is right **96.7%** of the time (5,127 images) |
| RAG retrieval, 49-document knowledge base, 22 test queries (preliminary labels) | hit@3 = **1.0**, recall@3 = **1.0**, MRR **0.92** (FAISS + MiniLM); **0.98** with a bge re-ranker |
| Automated software tests | **120 passing** |
| Old baseline model (13-class checkpoint) | could not recognise most crop classes (~11% on our set). **Do not headline this number**; it is not a like-for-like comparison. |
| Qwen advisor quality evaluation | **In progress.** Do not show a number. Show instead what is guaranteed by design: the validator checks schema, citations and "no dosages" on every answer. |

**Story to tell with the numbers:** "Our specialists were already ~97% accurate, but end-to-end accuracy was 77%. We found the bottleneck (routing), redesigned it, and measured the fix: 94.5%. We diagnose our own system like we diagnose crops, with data." Judges value this engineering maturity.

**Evaluation is a headline feature of this pitch, not a footnote.** The team wants to prove the product works. Give evaluation **two full slides** (method and results) plus a detailed appendix slide.

**How we evaluated (method, for the evaluation slide):**
- **Held-out test sets** the models never saw in training: PlantVillage (38 folders → 29 diagnosis classes) split into train / validation / **test**; cattle dataset stratified 70 / 15 / 15 (seed 42).
- **Metrics:** accuracy, **macro-F1** (treats rare diseases as equally important), **calibration (ECE)**, i.e. whether the confidence shown is trustworthy, confusion matrices, and **missed-disease counts** (safety).
- **Three levels tested:** each specialist alone → the router/gate → the **full end-to-end pipeline** the farmer actually uses.
- **Compared against baselines:** an off-the-shelf zero-shot model (CLIP) and our first routing design.
- **Retrieval tested separately:** does RAG fetch the right document for a query (hit@3, recall@3, MRR)?
- **Software:** 120 automated tests.

### A5. Tech stack (for the stack slide)
- **Edge AI / ML:** PyTorch training → MobileNetV3-Large (timm) fine-tuned with 3-stage gradual unfreezing, mixed precision → **ONNX Runtime** inference; Mixture-of-Experts gate; zero-shot vision-language domain router; image quality check (blur, exposure, contrast); multimodal fusion.
- **Generative AI:** **Qwen2.5-1.5B-Instruct + QLoRA fine-tune** (4-bit, PEFT); served as GGUF via **Ollama** / vLLM over an OpenAI-compatible API; **RAG** with sentence-transformers + **FAISS**; citation validator; **Google Gemini** fallback.
- **Speech / language:** Hindi input, AI4Bharat speech models, text-to-speech "Listen", full English/हिन्दी UI.
- **Application:** **Next.js** (React, TypeScript, Tailwind, shadcn/ui, Motion) web app; **FastAPI** backend; OTP phone login; admin portal.
- **Data:** SQLite farm memory (→ managed Postgres in production), FAISS vector index, weather context API.
- **Cloud / deployment:** containerised services; LLM server decoupled from the app; automatic fallback chain; health monitoring page.

### A6. Target users and market (qualitative, safe to state)
- **Primary users:** small and marginal farmers with mixed crop + livestock farms, low connectivity and a Hindi-first, low-literacy profile.
- **Paying customers (B2G/B2B):** state agriculture and animal-husbandry departments, Krishi Vigyan Kendras (KVKs), dairy cooperatives, FPOs, agri-input companies, crop/livestock insurers.
- Context facts: India has **~140 million+ farm holdings, mostly small and marginal**, and a very large livestock population. The **2022 lumpy skin disease outbreak** killed a very large number of cattle. → mark every figure `[VERIFY]` and add a source in small text; if a number can't be sourced, use the qualitative sentence instead.

---

## Part B: Design system (must match our app's "Field Journal" theme)

The app uses a warm, light, formal look: warm paper, leaf green, a turmeric/ochre accent and soil-dark ink. **Light theme only. No dark slides.**

### B1. Colours (use exactly these)
| Token | Hex | Use in deck |
|---|---|---|
| Paper (background) | `#FAF8F3` | Default slide background |
| Paper-2 | `#F3F0E8` | Cards, table header rows, alternating panels |
| Paper-3 | `#EBE6DA` | Subtle dividers, image frames |
| Surface | `#FFFFFF` | Cards on paper background |
| Ink | `#1F2A24` | Headlines, body text |
| Ink-2 | `#3E4B43` | Secondary text |
| Ink-3 | `#6B766F` | Captions, footnotes, sources |
| Line | `#E4DED1` | Borders, table lines |
| **Leaf (primary)** | `#2F5D3A` | Key words in titles, icons, primary shapes, section bars |
| Leaf-700 | `#234630` | Hover/emphasis, text on light leaf fills |
| Leaf-500 | `#3F7A4C` | Charts (series 1), secondary shapes |
| Leaf-100 | `#DFEADB` | Tinted highlight panels |
| Leaf-50 | `#EEF4EC` | Very light green panels (e.g. "solution" areas) |
| **Ochre (accent)** | `#C8963E` | Accent dot, key numbers, highlights (use sparingly) |
| Ochre-700 | `#9A6F24` | Ochre text on light backgrounds |
| Ochre-50 | `#FAF3E4` | Light accent panels ("MHTECHIN bridge" panel) |
| Sage | `#5B8C5A` | Chart series 2 |
| Brick | `#B5523B` | Problems, risks, "before" values only |
| Brick-50 | `#F7E6E0` | Light panel for the problem slide |

Rules: about 70% paper/white, 20% leaf greens, under 10% ochre. Brick only on the problem slide and on "before" numbers.

### B2. Typography
- **Headlines:** **Fraunces** (serif, semibold). If unavailable: Georgia.
- **Body / labels / numbers:** **Manrope** (sans). If unavailable: Calibri or Segoe UI.
- **Hindi text:** **Noto Sans Devanagari** (or Tiro Devanagari Hindi for display).
- Sizes: title 36–40 pt, subtitle 18–20 pt, body 16–20 pt (never below 14 pt), big stats 54–72 pt in Leaf or Ochre.
- Title style: sentence case, with one or two key words coloured Leaf, e.g. "A specialist for every **field** and every **animal**."

### B3. Logo (put it on every slide)
- **Mark:** a leaf that sees. A solid leaf shape in Leaf green `#2F5D3A` with a thin cream midrib and 4 veins, and an **ochre "iris" circle** (`#C8963E`, cream outline) near the top with a dark pupil (`#1F2A24`).
- **Wordmark:** "Agri**·**Vision" in Fraunces semibold, Ink colour, with the **middle dot in Ochre**.
- **Tagline:** "One farm. One app."
- **Placement:** large and centred on the title and closing slides. On all other slides, small (≈0.4 in) in the **top-left corner** with the wordmark, plus a slide number bottom-right in Ink-3.
- If the logo image file is attached, use it. Otherwise build it from this SVG (convert to PNG/EMF or redraw with shapes):

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" fill="none"><path d="M24 4C12 10 6 20 7.5 31.5C8.6 39.6 15 44 24 44C33 44 39.4 39.6 40.5 31.5C42 20 36 10 24 4Z" fill="#2f5d3a"/><path d="M24 12V44" stroke="#fbfaf5" stroke-width="2" stroke-linecap="round" opacity=".85"/><path d="M24 25L15.5 18.5M24 33L13 26.5M24 25L32.5 18.5M24 33L35 26.5" stroke="#fbfaf5" stroke-width="1.6" stroke-linecap="round" opacity=".55"/><circle cx="24" cy="20" r="5.2" fill="#c8963e" stroke="#fbfaf5" stroke-width="1.8"/><circle cx="24" cy="20" r="1.9" fill="#1f2a24"/></svg>
```

### B4. Visual language
- **Balance:** each slide has **one message**, **≤ 35 words of body text**, and **one strong visual** (screenshot, diagram, big number, or icon row). No paragraphs on slides; the detail lives in the speaker notes.
- **Icons:** thin line icons (Lucide style, the same family as the app) in Leaf green. Useful ones: leaf, sprout, beef/cow, wifi-off, scan-line, mic, languages, shield-check, book-open, database, cloud-cog, gauge, siren, users, map-pinned, trending-up.
- **Cards:** white or Paper-2 with rounded corners (radius ~14 px), 1 px Line border and a very soft shadow, the way the app's cards look.
- **No app screenshots and no photos.** The product is shown in a **live demo** in the middle of the presentation, and no farmer/field photos are available. Build the visuals from **flat vector illustrations and icon compositions** in the theme colours: e.g. a simple leaf + cow + phone illustration, a village/field line drawing, icon rows, diagrams, big numbers and charts. Never use stock-photo placeholders or robot/AI clichés.
- **Charts:** simple flat bar charts in Leaf/Sage, with "before" bars in Brick-tinted grey (see slide specs). Label values directly on the bars. No 3D, no gradients.
- **Organic touch:** optional very faint leaf/field-line illustration in a corner (Leaf-50) on the title, section and closing slides only.
- **Footer (optional):** "MHTECHIN Innovation Challenge 2026" in 10 pt Ink-3, bottom-left.
- **Transitions:** Fade or Morph only. At most one simple entrance animation per slide (e.g. big numbers appear). Nothing flashy.

---

## Part C: Presentation flow ("sandwich": slides → live app → slides)

Total target **≈ 7 minutes** (fits a 6–8 min video; for a live panel it can stretch to 10 with Q&A).

| # | Slide | Time | Section |
|---|---|---|---|
| 1 | Title | 0:00–0:10 | Opening |
| 2 | Hook: "One photo. One answer. Even offline." | 0:10–0:35 | Hook |
| 3 | The problem | 0:35–1:00 | Problem |
| 4 | Why solutions stall → MHTECHIN is the bridge | 1:00–1:25 | Strategic context |
| 5 | Our solution: Agri·Vision | 1:25–1:50 | Innovation |
| 6 | What makes us different (moat) | 1:50–2:15 | USP |
| 7 | How it works: 3-zone architecture | 2:15–2:45 | Solution design |
| 8 | Tech stack | 2:45–3:05 | Technology |
| 9 | **Live demo** (transition slide with link + QR) | 3:05–5:35 | **Demo (switch to the app)** |
| 10 | How we proved it works (evaluation method) | 5:35–5:55 | Evidence |
| 11 | Results: measured, not claimed | 5:55–6:30 | Evidence |
| 12 | Impact & business model | 6:30–6:55 | Business |
| 13 | Scale with MHTECHIN: roadmap & deployment | 6:55–7:15 | Scalability |
| 14 | Team | 7:15–7:20 | Team |
| 15 | Closing / the ask | 7:20–7:30 | Close |
| 16 | Appendix A: Evaluation detail (backup) | — | Q&A only |
| 17 | Appendix B: Safety, privacy & responsible AI (backup) | — | Q&A only |
| 18 | Appendix C: Production cloud architecture (backup) | — | Q&A only |

Speakers: the script uses neutral tags **Speaker 1 / Speaker 2 / Speaker 3**. **Do not print roles or titles on slides.** The team will assign names to speakers in the script doc themselves. Suggested split: Speaker 1 = story, problem, business, close; Speaker 2 = architecture, tech and evaluation; Speaker 3 = solution and live demo. Keep at least two voices to show team collaboration. (In Part D, "S1/S2/S3" means Speaker 1/2/3.)

---

## Part D: Slide-by-slide specification

> Format for each slide: **Title** (as shown on the slide) · **On-slide content** (exact text, keep it short) · **Visual** · **Speaker & script** (goes into speaker notes and the script doc) · **Presenter cue**.

### Slide 1: Title
- **On slide:** Large logo mark + "Agri·Vision" wordmark, centred. Tagline: **"One farm. One app."** Sub-line: "Specialist-grade crop & livestock health: offline, in Hindi, grounded by AI." Small line: "MHTECHIN Innovation Challenge 2026 · AgriTech · Generative AI". Team name `[FILL]`.
- **Visual:** Paper background, faint leaf-line illustration bottom-right, a thin Leaf bar at the bottom edge.
- **S1 script:** "Good [morning]. We are team [FILL], and this is Agri·Vision: one farm, one app."
- **Cue:** Smile, pause one beat, then advance.

### Slide 2: Hook
- **Title:** "Her tomatoes have spots. Her cow has lumps. The nearest expert is 40 km away." `[VERIFY distance or say "hours away"]`
- **On slide:** Three short lines, each with an icon: 🌿 *Crop disease spreading* · 🐄 *Livestock falling sick* · 📶 *One bar of signal*. Bottom, in Leaf, large: **"What if one photo was enough?"**
- **Visual:** Left 55%: a **flat vector illustration** (no photo) of a farmer figure beside a leaf with spots and a cow, with a phone showing one signal bar, in Leaf / Ochre / Paper tones and a warm, human feel. Right: the three icon lines.
- **S1 script:** "Meet a farmer in rural India. This week, brown spots are spreading across her tomato leaves, and her cow has developed lumps on its skin. The agronomist is hours away, the vet is further, and her phone shows one bar of signal. By the time help arrives, the crop is lost and the disease has reached the rest of the herd. We asked a simple question: what if one photo, and a few words in her own language, were enough?"
- **Cue:** Slow, human tone. This is the emotional anchor.

### Slide 3: The problem
- **Title:** "Farm health advice is **fragmented, online-only and English-first**."
- **On slide:** Three cards (Brick-50 background, Brick icon):
  1. **Fragmented**: separate apps and experts for crops and animals.
  2. **Online-only**: cloud apps fail where connectivity is weakest.
  3. **Unsafe & inaccessible**: English, text-heavy; generic chatbots can invent dosages.
  Below the cards, a one-line stat strip: "~86% of Indian farm holdings are small & marginal `[VERIFY + source]` · 2022 lumpy skin outbreak: ~1 lakh+ cattle deaths `[VERIFY + source]`".
- **Visual:** 3 cards in a row; stat strip in Ink-3 with source footnotes.
- **S1 script:** "Three barriers keep expert advice away from these farmers. First, fragmentation: crops and livestock live in different apps and different departments, yet most small farms have both. Second, connectivity: cloud-only tools fail exactly in the fields and sheds where they're needed. Third, access and safety: tools are English and text-heavy, and generic AI chatbots can confidently suggest the wrong treatment. The cost is real: lost harvests, and outbreaks like the 2022 lumpy skin epidemic."

### Slide 4: Why innovation stalls → MHTECHIN is the bridge
- **Title:** "Great agri-AI rarely leaves the lab."
- **On slide:** A left-to-right bridge graphic. Left bank, "**Lab prototype**": models on a laptop · no GPU serving · no scale. Right bank, "**Farmer's pocket**": reliable cloud · secure data · millions of users. The bridge in the middle is labelled **"MHTECHIN: cloud, deployment, enterprise engineering"** on an Ochre-50 panel. Under the left bank: "✅ Agri·Vision has already crossed the hardest part: working, measured AI."
- **Visual:** A simple flat bridge/arch illustration or a three-block arrow diagram.
- **S1 script:** "Here's the uncomfortable truth: most agricultural AI never leaves the lab. The model works on a laptop, but reaching millions of farmers needs GPU serving, cloud infrastructure, secure data handling and reliable deployment, which student teams and early startups rarely have. That's the gap MHTECHIN bridges. We've done the hard part: working, measured, safety-checked AI. With MHTECHIN's enterprise cloud and deployment expertise, Agri·Vision goes from prototype to product."

### Slide 5: Our solution
- **Title:** "A specialist for every **field** and every **animal**." (the app's own hero line)
- **On slide:** Three steps with icons (from the app's "How it works"): **Snap** (photograph a leaf, plant or animal; add symptoms if you like) → **Diagnose** (an auto-router picks the right AI specialist and fuses photo, words and sensor readings) → **Act** (clear treatment steps, in Hindi or English, saved to your private farm history).
- **Visual:** The three steps as large icon cards connected by arrows (camera → scan/brain → checklist). Optional on the right: a **simple vector phone outline** containing a stylised result card: a confidence ring "96%", a green "Answered on-device" chip and three short lines for "What to do now". It should be an illustration, not a screenshot.
- **S3 script:** "Agri·Vision is one app for the whole farm. Snap: the farmer photographs a leaf or an animal, and can add symptoms by typing or speaking in Hindi. Diagnose: an auto-router sends it to the right AI specialist, fusing the photo with their words and the animal's readings. Act: they get clear next steps in their language, and every check is saved to a private farm history."

### Slide 6: What makes us different
- **Title:** "Built for the last mile, not the lab."
- **On slide:** A 2×3 grid of icon tiles (≤ 6 words each):
  1. 📶✕ **Offline-first**: answers on-device
  2. 🌿🐄 **Crop + livestock**: one app
  3. 🗣️ **Hindi voice & text**: listen to advice
  4. 🛡️ **Grounded GenAI**: cited, validated, no dosages
  5. 🧠 **Explainable**: why, alternatives, confidence
  6. 🚨 **Outbreak watch**: regional early warning
  Small comparison strip below (optional table): *Generic chatbots / single-crop apps / Agri·Vision* versus Offline ✓, Livestock ✓, Hindi ✓, Citations ✓, Admin insights ✓. Only Agri·Vision has all the ticks. Name competitors by category only, never by brand.
- **S2 script:** "What makes us different? We work offline first; confident cases never need the internet. We cover crops and livestock in one app. The farmer can speak and listen in Hindi. Our generative AI is grounded: every recommendation cites a verified source and passes a safety validator that blocks drug dosages. Every answer explains itself. And because all checks roll up, administrators see outbreaks forming region by region. Generic chatbots and single-crop apps each cover a slice. We cover the whole farm."

### Slide 7: How it works (architecture)
- **Title:** "Three zones: fast on the edge, smart in the cloud, private at home."
- **On slide:** The attached image **`updated_architecture_diagram.png`** (the final diagram), placed as-is at ~85% of the slide width on a white card with a 1 px Line border. Only the slide title is added; no other text. Do **not** redraw it, because it already has its own colour legend. Its labels (use the same words in the script):
  - **① Farmer's Device, works offline:** inputs (Photo, Symptom text, Sensors, Region & season) → **Quality Check** (blur · exposure · contrast; reject → *Retake photo*) → **Domain Router** (crop vs livestock, zero-shot; reject → *Not a farm photo*) → **Mixture-of-Experts** (fine-tuned MobileNetV3 · ONNX): a learned MoE gate per domain, specialists *Row crops / Tree crops* and *Lumpy skin / Foot-and-mouth* → **Combiner** (most confident wins) → **Multimodal Fusion** (image + text + sensors) → **Confidence & Safety Gate** → Yes: **Offline Advice** (local KB) / Unsure or risky: escalate.
  - **② Cloud Advisory, only when needed:** **Privacy Filter** (personal data removed) → **Trusted Knowledge** (RAG · embeddings + FAISS) + **Context** (region & season, weather, farm history) → **Qwen2.5 Advisor** (LoRA fine-tuned · cites sources) → **Verify & Cite** (schema) → **Advice with Sources** → **Advice to Farmer** (English / Hindi). **Gemini Fallback** (dashed) if unavailable.
  - **③ Private Farm Memory:** **Farm Records** (SQLite, local) ↔ past cases → **My Farm History**; every case is saved.
  - Optional build (animation): reveal the three zone bands one at a time using three semi-transparent Paper-coloured cover rectangles that fade out on click. This helps the speaker walk through the zones.
  - If the image is not attached, redraw it with the same three bands and labels, with light blue / light amber / light green bands, teal for our fine-tuned models, a dashed grey Gemini box, yellow decision shapes and red reject boxes.
- **Visual:** the diagram is the slide.
- **S2 script:** "Under the hood there are three zones. Zone one runs on the farmer's device and works offline: a quality check rejects bad photos, a router decides crop or livestock and rejects non-farm photos, and a Mixture-of-Experts layer runs fine-tuned specialists for row crops, tree crops, lumpy skin and foot-and-mouth, exported to ONNX so they run on low-end phones. A combiner keeps the most confident specialist. We fuse the image with the farmer's words and the animal's readings, and a confidence-and-safety gate decides whether the answer can be given offline. Only uncertain, conflicting or safety-critical cases go to Zone two. There, personal data is stripped, retrieval pulls verified documents plus region, season, weather and the farm's own history, and our fine-tuned Qwen model writes a structured advisory. A validator checks the schema, verifies every citation and blocks dosages. If our model is unreachable, Gemini steps in, then a safe message, so the farmer never sees an error. Zone three is private farm memory, so advice improves season over season."

### Slide 8: Tech stack
- **Title:** "Enterprise-grade stack, built to scale."
- **On slide:** Five labelled columns or rows with small logos/icons (text labels are fine if logos aren't available):
  - **Edge AI / ML:** PyTorch · MobileNetV3 · Mixture-of-Experts · ONNX Runtime
  - **Generative AI:** Qwen2.5 + QLoRA · RAG (FAISS, sentence-transformers) · Gemini fallback · Ollama / vLLM
  - **Speech & language:** Hindi ASR (AI4Bharat) · text-to-speech · bilingual UI
  - **Application & APIs:** Next.js · TypeScript · Tailwind · FastAPI · OpenAI-compatible LLM API · OTP login
  - **Data & cloud:** SQLite → Postgres · FAISS vector index · weather API · containers · health monitoring
- **S2 script:** "Our stack mirrors a modern enterprise AI platform: PyTorch-trained, ONNX-deployed vision experts; a QLoRA-fine-tuned Qwen model with retrieval over a vector index; a Next.js front end on a FastAPI backend; and an OpenAI-compatible model API, so the same code runs on a laptop with Ollama or on a GPU cluster with vLLM, with no rewrite. That portability is what makes the move to MHTECHIN's cloud straightforward."

### Slide 9: Live demo (transition slide)
- **Title:** "Live demo"
- **On slide:** "Let's diagnose a real farm." A large button-style box with the **deployed URL** `[FILL: https://...]` and a **QR code** of that URL (generate one if you can; otherwise leave a `[QR]` placeholder). Below, the demo path as five small chips: **Farmer login → Diagnose a crop (offline) → Livestock case (cloud AI) → Farm history → Admin & outbreak watch**.
- **Visual:** a large logo mark next to a simple vector laptop/phone outline (empty screen with the logo inside). No screenshot.
- **S3 script:** "Enough slides. Let's see it working. I'll open our deployed app." → **Switch to the browser.** Follow the demo run-sheet in Part E. Come back to slide 10 afterwards (evaluation).
- **Cue:** Keep this slide visible for no more than 5 seconds. The app should already be open in another tab.

### Slide 10: How we proved it works
- **Title:** "We tested it like a product, not a demo."
- **On slide:** A left-to-right **4-step evaluation pipeline** of icon cards:
  1. 🗂️ **Held-out test data**: 5,433 crop images · 487 cattle images, never seen in training.
  2. 🔬 **Three levels**: each specialist → the router → the full farmer journey.
  3. 📏 **The right metrics**: accuracy · macro-F1 (rare diseases count equally) · calibration · missed diseases.
  4. ⚖️ **Against baselines**: off-the-shelf zero-shot AI · our own first design.
  Bottom strip (small chips): "RAG retrieval tested (hit@3 = 1.0)" · "120 automated tests passing" · "Safety: missed-disease counts tracked".
- **Visual:** 4 connected icon cards; the chips in Leaf-50.
- **S2 script:** "We didn't want to just show a demo that works once; we wanted proof. So we evaluated on held-out images the models never saw in training: over five thousand crop images and nearly five hundred cattle images. We tested at three levels: each specialist alone, the router, and the full journey a farmer actually experiences. We didn't stop at accuracy. We measured macro-F1, so rare diseases count as much as common ones; calibration, so the confidence we show can be trusted; and, most importantly for safety, how many sick animals we miss. We compared against an off-the-shelf AI model and against our own first design. Our retrieval layer and our software are tested too."

### Slide 11: Results
- **Title:** "Measured, not claimed."
- **On slide:**
  - Top row, **four big stat cards** (Leaf numbers, Ochre for the safety one): **97–98%** "specialist accuracy (crops)" · **94.5%** "crop diagnosis, end-to-end (29 classes)" · **89.5%** "livestock diagnosis, end-to-end" · **34 → 6** "missed lumpy-skin cases".
  - Bottom left: a before/after bar chart, "We found our bottleneck and fixed it": Crop 77.3% → **94.5%**; Livestock 83.6% → **89.5%**; plus one pair "vs off-the-shelf AI (livestock)": 53.0% → **89.5%**. Grey "before" bars, Leaf "after" bars, values labelled.
  - Bottom right: a small "Trust" card: "When the app says **≥ 90% sure**, it is right **96.7%** of the time" · "RAG finds the right source in the top 3: **100%**" (preliminary).
  - Footnote (Ink-3, 10 pt): "Held-out test sets: PlantVillage 5,433 images (29 classes); cattle 487 images. PlantVillage is lab-style imagery; field validation is the next step. Qwen advisor evaluation in progress."
- **S2 script:** "Here are the results. Our crop specialists reach 97 to 98 percent accuracy on their own. But our first end-to-end design scored only 77 percent. We traced the loss to routing, where images were sent to the wrong specialist, redesigned it to consult every expert in the domain, and measured again: 94.5 percent across 29 crop diagnoses. For livestock we went from 84 to almost 90 percent, and compared with an off-the-shelf AI model, that's a jump from 53 to 89.5 percent on the same images. Because we route disease-first, missed lumpy-skin cases dropped from 34 to 6; for a contagious disease, that's the number that matters most. And the confidence is honest: when the app says it's at least 90 percent sure, it's right about 97 percent of the time."

### Slide 12: Impact & business model
- **Title:** "Impact for farmers. A business for partners."
- **On slide (two columns):**
  - **Impact (left, Leaf-50 panel):** Faster diagnosis, in minutes not days · Fewer livestock deaths through early warning · Less pesticide misuse through the right advice · Voice-first for low-literacy users · A private health record for every farm.
  - **Business model (right, white card):**
    - **B2G:** state agri and animal-husbandry departments, KVKs, with outbreak dashboards and extension at scale.
    - **B2B:** dairy cooperatives, FPOs, agri-input companies and insurers, with consented, aggregated farm-health insights.
    - **Farmers:** free core diagnosis; premium advisory and alerts.
    - **Unit economics:** most checks are answered on-device (near-zero cost); cloud AI runs only for hard cases.
- **S1 script:** "For farmers, the impact is faster diagnosis, fewer animal deaths, less wasted pesticide, and advice they can listen to in their own language. For the business: governments and KVKs need early outbreak visibility and scalable extension, which is our admin portal. Cooperatives, input companies and insurers value consented, aggregated farm-health data. Farmers get the core free. And because most checks are answered on the device, our cost per user stays low; cloud AI is only paid for when a case is truly hard."

### Slide 13: Scale with MHTECHIN
- **Title:** "From prototype to a million farms, with MHTECHIN."
- **On slide:** A horizontal 3-stage roadmap (chevrons):
  1. **Now (prototype):** Next.js + FastAPI app · 4 ONNX experts · fine-tuned Qwen via Ollama · 49-doc knowledge base.
  2. **Pilot, 3–6 months (with MHTECHIN):** containerised cloud deployment · GPU autoscaled LLM serving (vLLM, multi-LoRA) · managed Postgres · field pilot with 1–2 KVKs / a dairy co-operative `[target]`.
  3. **Scale:** Android offline app · WhatsApp and IVR voice access · more languages and crops · MLOps (drift monitoring, agronomist feedback loop).
  Under the roadmap, one line on an Ochre-50 panel: "**What we bring:** working AI and domain depth. **What MHTECHIN brings:** cloud, deployment and enterprise scale."
- **S1 script:** "Here's how we scale together. Today we have a working, measured prototype. In a three-to-six-month pilot with MHTECHIN, we containerise and deploy on enterprise cloud, serve our fine-tuned models on autoscaling GPUs, move to a managed database and run a field pilot with a KVK or a dairy cooperative. Then we scale: an offline Android app, WhatsApp and voice-call access, more languages and crops, and continuous learning from agronomist feedback. We bring the AI and the domain depth; MHTECHIN brings the cloud and deployment muscle."

### Slide 14: Team
- **On slide:** Team name `[FILL]` as the heading. Member names `[FILL]` in a clean row of cards, **names only: no photos, no roles**. Each card has a leaf-green initial monogram circle (the first letter of the name) in place of a photo. Mark the team leader with a small "Team Leader" tag only if the team fills it in. One line below: "Built end-to-end: data, models, cloud AI, app and evaluation."
- **S1 script:** "We are team [FILL]: [names]. Together we built every layer, from data and model training to the cloud AI, the app and the evaluation you just saw."

### Slide 15: Closing / the ask
- **On slide:** Large logo. **"One farm. One app. Every farmer."** Below: "**Our ask:** partner with us to pilot Agri·Vision on MHTECHIN's cloud." Then the live app URL, GitHub URL `[FILL]`, contact email `[FILL]`, and the QR code again. Big "Thank you / धन्यवाद".
- **S1 script:** "Agri·Vision puts a crop and livestock specialist in every farmer's pocket: offline, in their language, grounded in verified knowledge. Our ask is simple: partner with us to pilot it on MHTECHIN's cloud. Thank you. धन्यवाद."
- **Cue:** Stop talking and hold the slide for 3 seconds (for the video) or open for questions (live panel).

### Slide 16: Appendix A, evaluation detail (backup, not presented)
- **Title:** "Evaluation detail"
- Two compact tables (Manrope 12–14 pt, Paper-2 header rows):
  - **Vision:** row crops 97.4% / macro-F1 0.965 / ECE 0.004 · tree crops 97.8% / 0.969 · lumpy-skin expert 93.6% · FMD expert 95.1% · crop end-to-end 77.3% → **94.5%** (ECE 0.136 → 0.037) · livestock end-to-end 83.6% → **89.5%** · CLIP zero-shot livestock 53.0%.
  - **Livestock safety (disease-first routing):** lumpy-skin cases predicted "healthy": 34 → 6 of 181.
  - **RAG (22 queries, k = 3, preliminary labels):** BM25 MRR 0.95 · FAISS + MiniLM MRR 0.92 · FAISS + bge re-ranker MRR **0.98**; hit@3 = 1.0 for all.
- Setup line: MobileNetV3-Large, 224 px, mixed precision, 3-stage gradual unfreezing, best epoch by validation macro-F1; hardest classes: strawberry leaf scorch, maize gray leaf spot.
- Honest limits: PlantVillage is lab-style imagery, so field validation is the next step; Qwen advisor evaluation is in progress.

### Slide 17: Appendix B, safety, privacy & responsible AI (backup)
Bullets: PII stripped before any cloud call · validator blocks drug dosages and verifies citations · safety-critical diseases are always escalated and always come with "consult a veterinarian or agronomist" · confidence shown to the user and "Not enough evidence" states instead of guessing · farm history private per farm · admin sees aggregated data · demo OTP mode is off in production.

### Slide 18: Appendix C, production cloud architecture (backup)
A two-column table, "Prototype today" vs "Production with MHTECHIN": Edge (web app → Android offline app) · API (FastAPI → gateway + auth + rate limits, containers) · LLM (Ollama → vLLM on autoscaling GPU, multi-LoRA) · Data (SQLite → managed Postgres + object storage, encryption) · Knowledge (49-doc FAISS → managed vector DB, KVK/ICAR-curated) · MLOps (manual → CI/CD, model registry, drift monitoring) · Channels (web → WhatsApp / IVR).

---

## Part E: Live-demo run-sheet (between slide 9 and slide 10, ≈ 2.5 min)

The demo follows the organiser's required path: **user entry → real-time AI processing → generated outputs → admin dashboard.** Put this run-sheet in the script doc as a table (Step · What to click · What to say · Fallback).

| # | Time | Screen / action | What to say (S3) | If it fails |
|---|---|---|---|---|
| 1 | 0:00–0:15 | **Landing page** ("A specialist for every field and every animal."). Toggle **हिन्दी** in the language switch, then back. | "This is our live app. It's fully bilingual; one tap and everything is in Hindi." | Skip the toggle. |
| 2 | 0:15–0:30 | **Login with phone number + OTP** (demo SMS shows the code on screen). Land on **Dashboard**: weather card, season, farm calendar, stats (Total checks, Healthy, Need attention, Answered offline). | "Farmers log in with just a phone number: no email, no password. The dashboard shows their farm at a glance: weather, season, and how many checks were answered offline." | Use a pre-logged-in tab. |
| 3 | 0:30–1:05 | **Diagnose → crop case.** Drop a *tomato early blight* leaf photo, keep "Detect automatically", type a note in Hindi: "पत्तियों पर भूरे धब्बे हैं" → **Analyse photo**. Point at the **live pipeline timeline** as steps light up. Result: disease name, **confidence ring**, **"Answered on-device"**, "What to do now", **"Why the AI decided this"**, other possibilities, seasonal note. Click **Listen**. | "I upload a leaf photo and add a note in Hindi. Watch the pipeline: quality check, routing, the expert team, fusion, the safety gate. Early blight, high confidence, answered on the device itself, no internet needed. It tells the farmer what to do now, explains why, shows alternatives, and can read it aloud." | Pre-recorded clip of the same case. |
| 4 | 1:05–1:45 | **Livestock case.** New check → *lumpy-skin cow* photo, symptoms ticked, animal readings **temperature high, feed intake low** → Analyse. The result shows **"Cloud expert"** route, **"Watch out"** + "consult a veterinarian", **Knowledge sources** with **"Citations verified"** badge, weather used. | "Now a cow. The farmer adds readings: high temperature, low feed intake. Lumpy skin is contagious, so the safety gate escalates it. Our fine-tuned Qwen model, grounded by retrieval, writes the advisory: every source is cited and verified, with no dosages and a clear instruction to call a vet." | If the LLM is slow: say "the cloud expert is generating" and cut the wait in editing. If it's down, the app falls back to Gemini/safe advice; say "and this is our automatic fallback working." |
| 5 | 1:45–1:55 | *(Optional)* Upload a **blurry/dark photo** → "We couldn't use this photo" → Retake. | "Bad photos are caught before they can cause a wrong diagnosis." | Skip. |
| 6 | 1:55–2:05 | **History** tab: list of past checks → open one. | "Every check becomes private farm memory, and the AI uses it next time." | — |
| 7 | 2:05–2:30 | **Admin portal** (separate login): **Platform overview**: KPIs (checks, active farmers, need attention, avg confidence, **answered offline %**, cloud escalations), daily chart, top conditions, regions, **"Outbreak watch"** alert. Then **System health**: Advisory AI (model, LLM server reachable, response time), Gemini fallback, Mixture of experts, model files. | "And this is the view for a state department or a cooperative. Live platform metrics, how many cases were solved offline, most reported diseases by region, and an outbreak alert when the same disease is reported three times in a region in a week. System health shows our AI stack live: our fine-tuned model, its response time, and the fallback." | Pre-opened tab; screenshots in the appendix. |
| — | 2:30 | **Switch back to the deck (slide 10).** | "So does it really work? Here is how we proved it." | — |

**Demo prep checklist (put it at the end of the script doc):**
- Seed the database with ~20–40 realistic demo checks across 3–4 states, so the admin charts and the Outbreak watch are populated (and say "demo data" if asked).
- Keep 3 photos on the desktop: tomato early blight, lumpy-skin cow, one blurry photo.
- Pre-warm the app and the LLM server (run each case once); keep app, admin and the deck open in separate tabs/windows.
- Browser zoom 110–125%, bookmarks bar hidden, notifications off, 1920×1080.
- Only say "fine-tuned Qwen" if the System health page shows our model as the one that answered.
- Hide the "Demo model — results are illustrative" banner risk: make sure real ONNX models are loaded (System health → Model files: none "Missing").

---

## Part F: Script document format (deliverable 2)

Create **`AgriVision_Pitch_Script.docx`** with the same theme (Fraunces headings in Leaf green, Manrope body, logo in the header):
1. **Cover:** logo, title "Agri·Vision: Pitch Script", event, team, total duration.
2. **Run-of-show table:** slide #, title, speaker, start–end time, cue.
3. **Per-slide script:** heading "Slide N: Title", speaker tag, the full script as above (you may polish the wording, but keep the facts and numbers identical), **[bold stage cues]** such as *[CLICK]*, *[SWITCH TO BROWSER]*, *[PAUSE]*, and an approximate word count (target ~140 words per minute).
4. **Demo run-sheet** (Part E as a table), with fallbacks.
5. **Q&A prep:** the questions below with 2–3 line answers.
6. **Checklists:** demo prep, recording tips (quiet room, headset mic, record in segments, captions on, export 1080p), final submission.

**Q&A to include:**
| Question | Answer direction |
|---|---|
| Why not just use ChatGPT/Gemini? | Offline-first; own fine-tuned model = cost control and privacy; RAG + validator = no hallucinated dosages; Gemini only as a fallback. |
| How accurate is it in real fields? | 94.5% / 89.5% end-to-end on held-out sets; PlantVillage is lab-style, so the next step is field validation with KVKs plus an agronomist feedback loop. Honest and confident. |
| How does it scale, and what does it cost? | Most checks are answered on-device; cloud load is proportional to hard cases only; stateless containers; OpenAI-compatible LLM API → vLLM autoscaling. |
| Why a 1.5B model? | Cheap and fast to serve (runs quantised even on CPU), fine-tuned for one structured task; RAG supplies the knowledge, not model size. |
| Data privacy? | PII stripped before the cloud; farm history private; admin sees aggregates; consent-based B2B data. |
| What's the revenue model? | B2G extension programmes, B2B co-ops/input/insurance insights, freemium for farmers. |
| What about other languages/crops? | Bilingual i18n architecture ready; KB and experts extend per crop/region (multi-LoRA). |
| What if the internet or our server is down? | Offline answer on the edge; cloud chain Qwen → Gemini → safe advice; the farmer never sees an error. |

---

## Part G: Final quality bar (check before returning the files)
- [ ] 15 main slides + 3 appendix slides, 16:9, light "Field Journal" theme, logo on every slide.
- [ ] No slide with more than ~35 words of body text; each slide has one clear visual.
- [ ] No screenshots and no photos: vector illustrations, icons, the architecture diagram and charts only.
- [ ] Evaluation gets two full slides (10 and 11) plus Appendix A.
- [ ] All numbers match Part A4 exactly; `[VERIFY]` / `[FILL]` placeholders are highlighted, not invented.
- [ ] Slide 9 has the URL + QR and clear "switch to demo" instructions.
- [ ] MHTECHIN appears on slides 1, 4, 8 (script), 13, 15.
- [ ] Speaker notes on every slide; the script doc matches the notes.
- [ ] Fonts: Fraunces + Manrope (or the stated fallbacks); colours from Part B only.
- [ ] No dark backgrounds, gradients, 3D charts or stock-cliché robots.

---

## Part H: Files attached with this brief
1. `updated_architecture_diagram.png`: the final architecture diagram; use it on slide 7 as-is.
2. `icon.svg`: the Agri·Vision logo mark (same as the SVG in Part B3).
3. Team details (in the chat message): team name, member names, the team leader, the deployed app URL, the GitHub URL and a contact email. Fill the `[FILL]` placeholders with these; leave anything not provided highlighted.
