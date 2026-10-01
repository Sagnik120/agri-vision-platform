# Agri·Vision: Pitch & Live Demo Script

**Format:** slides 1–5 → live demo (slide 6 is the hand-over) → slides 7–10.
**Speakers:** Speaker 1 (story and business), Speaker 2 (tech and results), Speaker 3 (demo). Assign names yourselves.
**Total time:** about 12 minutes (slides 1–6: 3:25 · live demo: 6:15 · slides 7–10: 2:45). If you have a limit of 8–10 minutes, use "Trim options" at the end (it gets you to about 9:30).
**Style:** plain, formal and warm. Speak slowly. Numbers are real, so don't round them up.

---

## 0. Before you record (fix these first)

| # | What | Why | Fix |
|---|---|---|---|
| 1 | **Turn on `both` routing.** Your System page shows "crop top1". Slide 7 claims 94.5% for crops, and that number is for `both` routing; top1 scored 77.3%. | Judges may open the System page. The demo must match the slide. | In the backend `.env` set `AGRIVISION_MOE_ROUTING=both`, restart the API, and check that the System page shows it. |
| 2 | **Clean demo data.** Dashboards and admin show "Mock disease" rows, "Demo Village", "Demo Farmer" and 0 healthy checks. | "Mock disease" looks like a fake demo on camera. | Use a fresh database, or delete the old Aug-17 rows. Then add 2–3 realistic checks (one *healthy* leaf), so the charts don't show 100% "need attention". |
| 3 | **Admin warning banner** ("admin password is still the default… Demo OTP mode is on"). | It appears at the top of the System page. | Set `ADMIN_PASSWORD` in `.env`. The OTP line is fine; if asked, say "demo mode, SMS is switched off". |
| 4 | **Landing-page copy is out of date.** The hero chip says "ViT · MobileNetV2", and the Architecture cards mention "MobileNetV2, ViT, EfficientNet-B3" and "Gemini reasons…". Your real system is MobileNetV3 experts + fine-tuned Qwen, with Gemini only as a fallback. | It contradicts your slides. | Best: change the text in `frontend/src/core/i18n/en.ts` and the hero chip (I can do it if you want). Otherwise **don't read those cards aloud**; the script below avoids them. |
| 5 | Warm up: run each demo case once, keep the LLM tunnel and the app open, and use two Chrome windows (farmer / admin). Zoom 110%, hide bookmarks, close WhatsApp. | First runs are slow. | — |
| 6 | Prepare three photos: a **tomato early-blight leaf** (will be low confidence → cloud), a **lumpy-skin cow** (high confidence → on-device), and one **healthy leaf** (optional). | The cases must behave as scripted. | Test them twice. |

### Deck corrections (I did not change the file; please fix these in PowerPoint)
1. **Slide 6, demo path chips:** they say "Diagnose a crop (offline)" and "Livestock case (cloud AI)". Your demo shows the opposite. Change them to **"Crop case → cloud escalation"** and **"Livestock case → on-device"**.
2. **Slide 5:** "OTP login" should be **"Phone + PIN login"**. OTP is used only at signup.
3. **Slide 2:** the small line "[VERIFY + source]" is still on the slide. Remove the tag, and remove either number you cannot source.
4. **Slide 7:** "Missed-disease counts tracked on every release" sounds like a release process you may not have. Better: "Missed-disease counts tracked in evaluation".
5. Slides 1, 6 and 10: add the link and QR (you said you will).

Everything else in the deck is consistent with the repo and with your evaluation report.

---

## 1. Slide script

### Slide 1: Title (0:00–0:15) · Speaker 1
*[Slide up. Pause one second.]*
"Good [morning]. We are team Binary Brains, and this is **Agri·Vision**. One farm, one app. A specialist for every field and every animal, working offline, in Hindi, and grounded in verified knowledge. Built for the MHTECHIN Innovation Challenge."

### Slide 2: The problem (0:15–1:10) · Speaker 1
"Picture a farmer in rural India. This week, brown spots are spreading on her tomato leaves, and her cow has lumps on its skin. The agronomist is hours away. The vet is even further. And her phone has one bar of signal.
Three things keep expert help away from her.
**First, it's fragmented.** Crops and animals sit in different apps and different departments, but most small farms have both.
**Second, it's online-only.** Cloud apps fail exactly where farmers need them.
**Third, it's unsafe and inaccessible.** It's in English, it's text-heavy, and general chatbots can confidently suggest the wrong treatment.
There is also a bigger gap. Most agricultural AI never leaves the lab. It works on a laptop, but reaching millions of farmers needs cloud infrastructure, GPU serving, secure data and deployment. That is the bridge MHTECHIN builds, and we've already crossed the hardest part: working, measured AI."

### Slide 3: The solution (1:10–1:50) · Speaker 3
"Our answer is one app for the whole farm, in three steps.
**Snap:** the farmer photographs a leaf, a plant or an animal, and can add symptoms by typing in Hindi or English.
**Diagnose:** an auto-router decides whether it's a crop or an animal, and sends it to the right specialist. It combines the photo, the farmer's words and the animal's readings.
**Act:** the farmer gets clear next steps in their own language, and every check is saved in a private farm history.
Under the hood we have four specialists: row crops, tree crops, lumpy skin disease and foot-and-mouth disease."

### Slide 4: What makes us different (1:50–2:25) · Speaker 2
"Five things set us apart.
It works **offline first**: confident answers come from the device itself.
It covers **crops and livestock** in one app.
It speaks **Hindi**, in text and voice.
Its generative AI is **grounded**: every answer cites a verified source and passes a safety validator that blocks drug dosages.
And it is **explainable**: the farmer sees why, what else it could be, and how sure the AI is.
On top of that, the same data gives administrators an early warning for disease outbreaks. Chatbots and single-crop apps each cover one slice of this. We cover the whole farm."

### Slide 5: Architecture and stack (2:25–3:15) · Speaker 2
*[Point to each zone on the diagram.]*
"Here is how it works, in three zones.
**Zone one runs on the farmer's device, and works offline.** A quality check rejects blurry photos. A router separates crops from animals and rejects non-farm photos. Then a Mixture-of-Experts layer runs our fine-tuned MobileNetV3 specialists, exported to ONNX so they run on low-end phones. It fuses the photo with text and sensor readings, and a confidence-and-safety gate decides: is this answer good enough to give offline?
**Zone two is used only when needed**: uncertain, conflicting or risky cases. Personal data is removed first. Then retrieval pulls verified documents from our knowledge base, together with the farm's region, season, weather and history. Our fine-tuned Qwen model writes the advisory, and a validator checks the format and every citation. If our model is unreachable, Gemini steps in, so the farmer never sees an error.
**Zone three is private farm memory.** Every case is saved, so advice gets better season after season.
The stack is modern and portable: PyTorch and ONNX, a QLoRA-fine-tuned Qwen, FAISS retrieval, Next.js and FastAPI, all behind a standard model API."

### Slide 6: Live demo hand-over (about 0:10) · Speaker 3
"Enough slides. Let's see it working. This is our live, deployed app."
*[Switch to the browser. Full demo script is in section 2.]*

---

## 2. Live demo script (about 6:15; each part has its own timer)

**Speaker 3 drives. Keep the mouse slow and deliberate; the animations are part of the show.** Screen names match your screenshots.

### Part A: Landing page (0:00–0:50)
*[Landing page open. Let the hero animation run for 2 seconds.]*
"This is the Agri·Vision home page. On the right, the scanning leaf shows what the app does: look at a photo, and answer in Hindi or English." *[Click the EN / हि toggle, then back to EN.]* "The whole app switches language with one tap.
At the top there is a live status, 'Cloud assist ready', which tells the farmer that the AI service is available."
*[Scroll slowly.]* "Here, the app lists the conditions it recognises, from crop diseases to lumpy skin and foot-and-mouth disease.
**Why it matters**: three real barriers: networks that drop, English-only apps, and five apps for one farm." *[Click the carousel arrow once.]*
**How it works**: Snap, Diagnose, Act." *[Scroll.]*
**Architecture**: three zones: on the device, cloud only when needed, and private farm memory. *(Don't read the text on the cards.)*
"And finally, it takes less than a minute to create an account." *[Click "Create free account" or "Log in".]*

### Part B: Login (0:50–1:10)
*[Login page. Farmer tab is selected.]*
"Farmers sign in with just a phone number and a four-digit PIN. No email, no long password. New farmers sign up in three short steps with a one-time code. There is also a separate Admin login, which we'll see later."
*[Type the phone number and PIN. Click Log in.]*

### Part C: Farmer dashboard (1:10–2:00)
*[Dashboard loads.]*
"Welcome to the farm dashboard. It greets the farmer by name and already knows the state, Rajasthan, and the season, Kharif. These two things tailor the advice.
At the top: **start a new check**. Below are four numbers: total checks, healthy, need attention, and **answered offline**.
Then the **farm calendar**. Each day is colour-coded: green for healthy, amber for watch, red for attention. Tap a day to see the checks.
Next to it is the **weather**, from Open-Meteo, with a five-day forecast and a practical tip: for example, 'good conditions for spraying today'.
Below, the **recent checks**, each with a photo, a confidence score and a badge that shows where the answer came from: *Answered on-device* or *Cloud expert*. And a split of crops versus livestock.
Now let's do a real check." *[Click "New check".]*

### Part D: New check, case 1 (crop, low confidence → cloud) (2:00–3:10)
*[The New check page.]*
"The farmer uploads a photo, or uses the camera. They can let the app detect the type automatically, or choose crop or livestock. They can tick symptoms and describe the problem in their own words, in Hindi or English."
*[Upload the tomato leaf. Keep "Detect automatically". Type: "पत्तियों पर भूरे धब्बे हैं". Tick "Spots on leaves". Click Analyse.]*
"Watch the pipeline." *[Wait while the steps animate. Point at them.]* "Quality check, routing to the crop experts, the expert team, fusion with the farmer's words, and the safety gate."
*[Result appears.]* "The specialist suggests early blight, but with only about 68% confidence. That is below our threshold, so the app **does not guess**. It escalates to the cloud. See the badge: **Cloud expert**.
Here, our fine-tuned Qwen model, together with retrieval, writes the advice: **what to do now**, **why the AI decided this**, other possibilities, and the **knowledge sources**, with a *Citations verified* tag. Every source is real, and there are no drug dosages. The farmer can press **Listen** to hear it read aloud." *[Click Listen for 3–4 seconds, then stop.]*

### Part E: New check, case 2 (livestock, high confidence → on-device) (3:10–3:50)
*[Click "Check another". Upload the lumpy-skin cow photo. Type "Cow has lumps on body". Open "Animal readings": set temperature high, feed intake low. Click Analyse.]*
"Now a cow. The farmer adds readings: high temperature, low feed intake." *[Result appears.]* "Lumpy skin disease, **99% confidence**, answered **on the device**, with no internet. Because this is a contagious, reportable disease, the result also carries a clear warning to contact a veterinarian. High confidence means speed; risky cases always get a 'consult an expert' message."

### Part F: Farm history (3:50–4:15)
*[Click "Farm history".]*
"Every check is saved here as private farm history. There's a **filter**: all, crops, livestock, healthy, attention, cloud." *[Open the filter, choose "Cloud", then back to "All".]* "And a search box." *[Click one record.]* "Open any record to see the full advice again. This history is not just a log: it goes back to the AI as context for the next check."

### Part G: Settings and logout (4:15–4:35)
*[Click "Settings".]*
"In settings, the farmer sees their profile, sets the **region**, which tailors advice to local seasons, and picks the **language**: English or Hindi. And this panel shows the system status: AI server ready, real AI models, and our fine-tuned Qwen as the advisory engine."
*[Click "Log out".]*

### Part H: Admin portal (4:35–6:15)
*[Login page. Switch to the "Admin" tab. Log in.]*
"Now the other side: the administrator, for example a state department, a KVK or a dairy cooperative.

**Overview.** This is the live picture of every farm, check and AI decision. At the top, the **Outbreak watch**: it fires when the same disease is reported three or more times in one region in a week. Here: lumpy skin disease, Rajasthan, four cases. That is early warning that no single farmer could see.
Below, the headline numbers: checks, active farmers, cases needing attention, average AI confidence, **percent answered offline**, and cloud escalations. You can switch between 7, 30 and 90 days, and export everything to CSV. *(Scroll slowly.)* Below are checks per day, the crop / livestock mix, the most reported conditions, and regions. The **confidence distribution** shows where the models struggle, and the hourly chart shows when farmers use the app.

**All checks.** *(Click "All checks".)* Every diagnosis across all farms, with filters for type, route, outcome, region and date, plus search and export. *(Click one row.)* Each one opens to the full photo, evidence and advice, so an expert can review it.

**Farmers.** *(Click "Farmers".)* Everyone registered, with their region, number of checks, and how many need attention. You can sort by activity or by attention. Phone numbers are masked, so privacy is built in.

**System health.** *(Click "System".)* And finally, the health of our AI. The advisory backend is our fine-tuned Qwen model, served from Hugging Face, and the LLM server is ready. Gemini fallback is ready. The vision pipeline is running real models with the Mixture-of-Experts, plus weather context and Hindi translation. If anything goes down, we see it here in seconds."

*[Switch back to the slides. Go to slide 7.]*
"So does it really work? Here is how we proved it."

---

## 3. Closing slides

### Slide 7: Validation (about 1:00) · Speaker 2
"We tested it like a product, not a demo. Everything here is measured on held-out images that the models never saw in training: 5,433 crop images and 487 cattle images.
Our crop specialists reach **97 to 98 percent** accuracy on their own. The first end-to-end design scored only 77 percent, so we traced the loss to routing, redesigned it, and measured again: **94.5 percent across 29 crop diagnoses**. Livestock went from 84 to **89.5 percent**. Compared with an off-the-shelf AI model on the same cattle images, that is a jump from 53 to 89.5 percent.
The most important number is this one: missed lumpy-skin cases fell from **34 to 6**. For a contagious disease, that is what matters.
And the confidence is honest: when the app says it is at least 90 percent sure, it is right about 97 percent of the time. Retrieval finds the right source in the top three every time, and we have 120 automated tests passing.
We also want to be clear about the limits: this data is lab-style imagery, so the next step is field validation, and our Qwen advisor evaluation is still in progress."

### Slide 8: Impact and business model (about 0:40) · Speaker 1
"For farmers, the impact is diagnosis in minutes instead of days, fewer animal deaths, less pesticide misuse, and advice they can listen to in their own language.
For the business: **governments and KVKs** need early outbreak visibility and extension at scale, which is our admin portal. **Cooperatives, input companies and insurers** value consented, aggregated farm-health insights. Farmers get the core service free, with premium advisory and alerts on top.
And because most checks are answered on the device, our cost stays low. We pay for cloud AI only when a case is truly hard. Safety is built in: personal data is removed before any cloud call, and risky cases always say 'consult a vet or agronomist'."

### Slide 9: Roadmap with MHTECHIN (about 0:35) · Speaker 1
"Today, we have a working, measured prototype. In a three-to-six-month pilot with MHTECHIN, we containerise and deploy on enterprise cloud, serve our fine-tuned models on autoscaling GPUs, move to a managed database, and run a field pilot with a KVK or a dairy cooperative. Then we scale: an offline Android app, WhatsApp and voice-call access, more languages and more crops.
We bring the AI and the domain depth. MHTECHIN brings cloud, deployment and enterprise scale."

### Slide 10: Thank you (about 0:30) · Speaker 1
"Agri·Vision puts a crop and livestock specialist in every farmer's pocket: offline, in their language, and grounded in verified knowledge. Our ask is simple: partner with us to pilot it on MHTECHIN's cloud.
We are Sagnik Chandra, Shrusti Jain and Arjun Baidya. The live app and our code are here, on screen. Thank you. धन्यवाद."
*[Hold the slide for 3 seconds.]*

---

## 4. Quick Q&A answers (one or two lines each)

- **Why not just use ChatGPT or Gemini?** Ours works offline first, runs our own fine-tuned model for privacy and cost, and grounds every answer in cited sources with a validator. Gemini is only a fallback.
- **How accurate is it in real fields?** 94.5% (crops) and 89.5% (livestock) end-to-end on held-out data. It is lab-style imagery, so field validation with KVKs is the next step. We say this openly.
- **Why a small model?** A 1.5B model is cheap and fast to serve, even on CPU. Retrieval supplies the knowledge, so model size matters less.
- **Privacy?** Personal data is removed before any cloud call, farm history is private, admin phone numbers are masked, and B2B data would be consented and aggregated.
- **What if the internet or the model server is down?** Confident cases still work offline. The cloud chain falls back from Qwen to Gemini to a safe message.
- **How do you scale?** Most checks never leave the device. Cloud load grows only with hard cases. The model API is standard, so the same code moves from Ollama to autoscaling GPUs.

## 5. Trim options (if you must cut time)
- Drop Part G (Settings) and the scrolling in Part A: saves about 45 seconds.
- In the admin portal, show only Overview and System: saves about 40 seconds.
- Shorten Slide 4 to the three bullets you like most: saves about 15 seconds.
- Skip the Listen button and the Farm history filter: saves about 20 seconds.
All together this gets you to about 9:30. Don't cut the two check cases, the Outbreak watch or the results slide.
