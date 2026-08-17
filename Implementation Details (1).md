# **IMPLEMENTATION DETAILS** 

## **1. Final prototype architecture to implement** 

I would freeze the implementation to this: 

FARMER INPUT 

│ ┌───────────────┼───────────────┐ ↓               ↓               ↓ 📷 IMAGE         🎙 VOICE        🐄 SENSOR │               │               │ │         Hindi IndicConformer  │ │               ↓               │ │          TEXT / SYMPTOMS      │ │               │               │ ↓               ↓               ↓ IMAGE SPECIALIST   TEXT EVIDENCE   SENSOR EVIDENCE │               │               │ ↓               └───────┬───────┘ Crop/Livestock Expert          │ │                       │ └───────────┬───────────┘ ↓ LATE EVIDENCE FUSION ↓ CONFIDENCE & SAFETY GATE /             \ HIGH              LOW ↓                 ↓ LOCAL ADVISORY      CLOUD ESCALATION │                 │ │          Gemini + RAG + Farm │               Context 

IMAGE SPECIALIST   TEXT EVIDENCE   SENSOR EVIDENCE 

│                 │ └────────┬────────┘ 

↓ 

ACTIONABLE ADVISORY 

↓ 

Hindi TTS / Text 

↓ 

FARMER 

↓ 

PRIVATE FARM MEMORY 

The important architectural distinction is: 

**The image specialist does not consume the text. The fusion layer consumes the outputs/evidence from different modalities.** 

## **2. Freeze the technology choices before coding** 

I recommend this exact stack. 

|**Component**|**Prototype choice**|
|---|---|
|UI|Streamlit|
|Backend|Python/FastAPI|
|Crop specialist|Pretrained PlantVillage MobileNetV3|
|Livestock specialist|Pretrained cattle-disease model|
|ASR|**AI4Bharat IndicConformer Hindi — 30M**|
|Text evidence|Lightweight symptom extraction/rules|
|Sensor|Simulated sensor + rule-based anomaly detection|
|Fusion|Rule/score-based late fusion|
|Confidence gate|Threshold + modality agreement|
|Local advisory|Local JSON/knowledge mapping|
|Cloud LLM|Gemini API|
|RAG|FAISS/Chroma + curated trusted KB|
|Farm memory|SQLite|



**Component Prototype choice** Hindi TTS AI4Bharat Hindi FastPitch + HiFi-GAN first TTS fallback IndicF5 

Privacy-preserving learning **Not implemented** 

AI4Bharat's official model page describes IndicConformer as a **30M-parameter Conformer ASR model designed for real-time Indian-language ASR and deployable on Android** , which makes it particularly well aligned with your offline-first claim. (AI4Bharat Models) 

## **3. STEP 0 — Create the project skeleton** 

Before downloading random models or writing UI, create: 

agri_vision/ 

│ ├── app/ │   └── streamlit_app.py │ ├── backend/ │   └── api.py │ ├── models/ 

│   ├── crop_expert/ 

│   ├── livestock_expert/ │   ├── asr/ │   └── tts/ │ 

├── experts/ 

│   ├── crop_expert.py 

│   ├── livestock_expert.py 

│   ├── sensor_expert.py 

│   └── router.py │ 

├── multimodal/ 

│   ├── text_evidence.py 

│   ├── fusion.py 

│   └── confidence.py │ ├── cloud/ │   ├── gemini_client.py │   ├── rag.py │   └── prompts.py │ ├── farm_memory/ │   ├── database.py │   └── models.py │ ├── knowledge/ │   ├── crop/ │   └── livestock/ │ ├── demo_data/ │   ├── crop/ │   ├── livestock/ │   ├── audio/ │   └── sensor/ │ ├── config.py ├── requirements.txt └── README.md 

**Don't build the whole folder structure into a complicated software architecture.** This is simply to keep the 15-hour codebase manageable. 

## **4. STEP 1 — Establish the common data contract** 

This is surprisingly important. 

Every expert should return the same format. 

For example: 

{ 

"domain": "crop", 

"input_type": "image", 

"prediction": "Tomato Early Blight", "confidence": 0.91, "top_k": [ ["Tomato Early Blight", 0.91], ["Tomato Late Blight", 0.05], ["Healthy", 0.04] ] } ASR returns: 

{ 

"text": "पत्ति�यों� पर भू�र� धब्बे� हैं�", "language": "hi", "confidence": None 

} Sensor returns: 

{ "domain": "livestock", "temperature": 39.8, "activity": "low", "feed_intake": "low", "anomaly": True 

} 

Then fusion receives all of these. 

This prevents the frontend from becoming tightly coupled to individual models. 

## **5. STEP 2 — Implement the Hindi IndicConformer ASR first** 

This is one of the highest-priority components because it establishes the **offline voice path** . 

AI4Bharat's IndicConformer collection provides a dedicated Hindi model, and its official repository provides monolingual checkpoints for Hindi. (Hugging Face) 

AI4Bharat specifically describes the 30M IndicConformer as intended for real-time ASR and Android deployment. (AI4Bharat Models) 

## **Target pipeline** 

audio.wav 

↓ 

IndicConformer Hindi 

↓ 

Hindi transcript 

↓ text_evidence.py 

## **6. Do NOT integrate it into Streamlit immediately** 

First make a standalone test: 

test_asr.py 

Input: 

demo_data/audio/crop_problem.wav 

Output: 

पत्ति�यों� पर भू�र� धब्बे� हैं� और पत्ति�यों�� प�ली� हैं� रहैं� हैं�। 

You need to prove: 

- model loads 

- audio preprocessing works 

- transcription works 

- inference time is acceptable 

- Hindi output is usable 

Only then integrate it. 

## **7. Use a fixed Hindi demo sentence** 

Don't rely on spontaneous speech initially. 

Record 3–4 clean examples: 

## **Crop** 

"टमा�टर की� पत्ति�यों� पर भू�र� धब्बे� हैं� और पत्ति�यों�� प�ली� हैं� रहैं� हैं�।" 

## **Livestock** 

"गा�यों आज कीमा खा�ना� खा� रहैं� हैं� और उसकी� गाति#ति$धिध कीमा हैं�।" 

## **Healthy** 

"प&ध� स्$स्थ दि*खा�ई *� रहैं� हैं�।" 

## **Ambiguous** 

"पत्ति�यों� मा, की- छ बे*ली�$ दि*खा�ई *� रहैं� हैं�।" 

These give you controlled test cases. 

## **8. STEP 3 — Build the text evidence extractor** 

This does **not** need another LLM. 

Create: 

multimodal/text_evidence.py 

Input: 

"टमा�टर की� पत्ति�यों� पर भू�र� धब्बे� हैं� और पत्ति�यों�� प�ली� हैं� रहैं� हैं�।" 

Output: 

{ "symptoms": [ 

"brown_spots", "yellow_leaves" ], 

"crop": "tomato", 

"severity_hint": "moderate" 

} 

## **9. Hindi symptom mapping** 

Create a small dictionary. 

For example: 

HINDI_SYMPTOMS = { 

"भू�र� धब्बे�": "brown_spots", 

"भू�र� तिनाशा�ना": "brown_spots", 

"प�ली� पत्ति�यों��": "yellow_leaves", 

"पत्ति�यों�� प�ली�": "yellow_leaves", 

- "सफे�* प�उडर": "white_powder", 

- "पत्ति�यों�� मा-ड़": "leaf_curl", 

"की�ड़�": "insects", 

"मा-रझा�": "wilting", 

## } 

And English equivalents: 

ENGLISH_SYMPTOMS = { 

"brown spots": "brown_spots", 

"yellow leaves": "yellow_leaves", 

"white powder": "white_powder", 

"wilting": "wilting", 

"insects": "insects" 

} 

This is enough for a prototype. 

## **10. Why I'm recommending rules here** 

Because your innovation is **not NLP** . 

Your innovation is: 

multimodal agricultural decision architecture. 

Don't waste your limited time training a Hindi symptom classifier. 

The rule-based extractor is: 

- deterministic 

- fast 

- offline 

- explainable 

- easy to debug 

And you can later replace it with a learned text encoder. 

## **11. STEP 4 — Implement crop specialist** 

Use the pretrained crop model you selected earlier. 

The basic pipeline: 

Image 

↓ 

Resize / normalize 

↓ 

MobileNetV3 

↓ Softmax ↓ Top-3 predictions Return: { "domain": "crop", "prediction": "Tomato Early Blight", "confidence": 0.91, "top_k": [...] } 

## **12. STEP 5 — Implement livestock specialist** 

Same interface: Livestock Image ↓ EfficientNet-B3 ↓ Prediction ↓ Confidence For example: { "domain": "livestock", "prediction": "Lumpy Skin Disease", "confidence": 0.87 

} Don't add text to this model either. 

## **13. STEP 6 — Implement the task router** 

The router should determine: 

Crop or livestock? 

For your prototype, the easiest reliable mechanism is: 

## **Explicit UI selection** 

[ Crop ] [ Livestock ] 

Then: 

if domain == "crop": 

crop_expert(image) 

else: 

livestock_expert(image) 

## **Why not build an image domain classifier?** 

Because it's unnecessary. 

Your architecture says **Task Router** , not necessarily that the router has to be a neural network. In a real product, it could be: 

- UI selection 

- metadata 

- lightweight classifier 

- learned router 

For the prototype, explicit selection is reliable. 

## **14. But you should still demonstrate "dynamic routing"** 

Have the UI say: 

Detected task: 

- 🐄 Crop Disease Analysis 

Expert selected: 

Crop Disease Expert 

or: 

Detected task: 

- 🐄 Livestock Health Analysis 

Expert selected: 

Livestock Health Expert 

So the judge sees the architecture without you risking a bad automatic router. 

## **15. STEP 7 — Implement the sensor expert** 

Don't connect physical IoT hardware unless you already have working hardware. 

Create a simulated sensor panel: 

Livestock ID: COW-017 

Temperature: 39.8 °C Activity: 28% Feed intake: 42% Movement: Low Then: 

if temperature > threshold: temperature_alert = True 

if activity < threshold: activity_alert = True 

if feed_intake < threshold: feeding_alert = True Output: 

{ "temperature_alert": True, "activity_alert": True, "feeding_alert": True, "anomaly": True } 

## **16. STEP 8 — Implement late evidence fusion** 

This is the **key new component** . 

Create: 

multimodal/fusion.py 

Inputs: 

Visual prediction 

+ 

Text evidence 

+ 

Sensor evidence 

## **17. Don't make fusion unnecessarily mathematical** 

For your MVP: 

## **Start with visual confidence as the base.** 

Example: 

Image: 

Early Blight = 0.88 

Then text evidence: 

brown spots → supports Early Blight 

yellow leaves → supports Early Blight 

Then: 

Agreement = YES 

Result: 

Final confidence = HIGH 

## **18. Example fusion logic** 

Conceptually: 

score = image_confidence 

if text_supports_prediction: score += 0.10 

if text_conflicts_with_prediction: 

score -= 0.20 

score = min(score, 0.99) 

Then: 

if score >= 0.75: 

route = "local" 

else: 

route = "cloud" 

This is not intended to be scientifically calibrated. It's an MVP decision mechanism. 

## **19. But don't let text arbitrarily override the image** 

This rule is important. 

## **Example** 

Image: Early Blight = 0.91 

Text: 

"There are brown spots." → agreement. 

## **But:** 

Image: Early Blight = 0.53 Late Blight = 0.41 Text: 

"There is white powder." → ambiguous/conflicting. Therefore: 

## **Cloud escalation.** 

This makes your system safer. 

## **20. STEP 9 — Add explicit "evidence agreement"** 

Have fusion output: 

{ 

"prediction": "Tomato Early Blight", 

"visual_confidence": 0.88, 

"text_support": True, 

"sensor_support": None, 

"evidence_agreement": "high", 

"final_confidence": 0.93, 

"route": "local" 

} 

This is excellent for your UI because you can show: 

## **Why did the AI make this decision?** 

## **21. STEP 10 — Build the confidence & safety gate** 

The gate should have **three inputs** : 

## **A. Model confidence** 

0.88 

## **B. Evidence agreement** 

High 

## **C. Input quality** 

Good 

Then: 

HIGH CONFIDENCE 

= 

confidence ≥ threshold AND 

evidence consistent 

AND 

input quality acceptable Otherwise: CLOUD 

## **22. This gives you a very good demo visualization** 

## **Local case** 

┌───────────────────────────────┐ 

✓ │ LOCAL DECISION              │ 

│                               │ │ Tomato Early Blight           │ │ Confidence: 93%               │ │                               │ ✓ │ Visual evidence: │ ✓ │ Voice evidence: │ ✓ │ Image quality: │ │                               │ │ No cloud required             │ └───────────────────────────────┘ 

## **Cloud case** 

┌───────────────────────────────┐ 

│ ⚠ CLOUD ESCALATION            │ │                               │ │ Local confidence: 54%         │ │ Evidence: conflicting         │ │                               │ │ → Sending evidence to cloud   │ └───────────────────────────────┘ 

This is one of the most valuable things you can show the judges. 

## **23. STEP 11 — Build local actionable advisory** 

For high-confidence cases, don't call Gemini. 

Create: 

knowledge/local_advisories.json 

Example: 

{ 

"Tomato Early Blight": { 

"summary": "Possible early blight detected.", 

"actions": [ 

"Remove severely affected leaves.", 

"Avoid overhead irrigation.", 

"Follow locally approved crop-protection guidance." 

], 

"warning": "Consult an agricultural expert if symptoms spread." 

} 

} Then: 

Local diagnosis 

↓ 

Local knowledge ↓ 

Actionable advisory 

This means your **high-confidence path is genuinely offline** . 

## **24. STEP 12 — Add Hindi TTS** 

Here's the correction to your requested specification: 

## **IndicConformer Hindi ≠ TTS** 

IndicConformer is specifically an **ASR** model. AI4Bharat's current model collection separately lists IndicF5 and Indic Parler-TTS under TTS. (Hugging Face) 

For your prototype, I recommend this order: 

## **Option 1 — AI4Bharat Hindi FastPitch + HiFi-GAN** 

AI4Bharat's Indic-TTS project provides pretrained TTS models for 13 Indian languages, including Hindi, with a FastPitch acoustic model and HiFi-GAN vocoder. Its repository gives direct inference using downloaded Hindi checkpoints. (GitHub) 

This is the first one I'd test because it is a **monolingual Hindi TTS** , rather than a large multilingual generative TTS system. 

## **25. Option 2 — IndicF5** 

If the old Indic-TTS setup becomes painful, try: 

## **IndicF5** 

It supports Hindi and 10 other Indian languages and is MIT licensed. (Hugging Face) 

However, it is around **0.4B parameters** , according to AI4Bharat's current model listing, so it is not my first choice for your "lightweight edge" story. (Hugging Face) 

## **26. Option 3 — Indic Parler-TTS** 

Technically impressive, but **don't use it for this 15-hour prototype unless everything else is already finished** . 

The current AI4Bharat Indic Parler-TTS checkpoint supports Hindi and many other Indian languages, but the model file shown in the repository is about **3.75 GB** , and the model is gated. (Hugging Face) 

That's unnecessary complexity. 

## **27. There is another lightweight Hindi TTS possibility** 

I found a 2026 community project called **vani-tts** , described as a lightweight on-device Hindi TTS system using AI4Bharat IndicVoices, ONNX export, and offline CPU real-time inference. (GitHub) 

This is potentially very attractive for your architecture, but because it is a **third-party/community project rather than an official AI4Bharat model** , I would use it only if: 

1. installation is easy, 

2. license is acceptable, 

3. output quality is good enough. 

Don't make it your critical dependency. 

## **28. STEP 13 — Build the cloud escalation** 

Only after local processing works. 

Cloud request should contain: 

{ 

"domain": "crop", 

- "image_prediction": "Tomato Early Blight", 

- "visual_confidence": 0.54, 

- "farmer_text": "पत्ति�यों� पर भू�र� और सफे�* धब्बे� हैं�", 

- "text_evidence": [ 

"brown_spots", 

"white_powder" 

], 

"sensor_data": null, 

- "farm_history": "...", 

- "retrieved_knowledge": "..." 

## } 

Then Gemini gets: 

**Current evidence + farm context + trusted knowledge** 

## **29. STEP 14 — Build the RAG knowledge base** 

Don't make this huge. 

Create around: 

## **Crop** 

- tomato early blight 

- tomato late blight 

- potato early blight 

- potato late blight 

- maize rust 

- maize leaf blight 

## **Livestock** 

- lumpy skin disease 

- foot-and-mouth disease 

- abnormal temperature 

- abnormal activity 

## **General** 

- image quality 

- when to consult expert 

## **30. Each knowledge entry should have this structure** 

Condition: 

Tomato Early Blight 

Symptoms: 

... 

Visual indicators: 

... 

Recommended actions: 

... 

Prevention: 

... 

When to seek expert: 

... 

Source: 

<official/trusted source> 

Don't let Gemini invent the knowledge. 

The retrieved material should be the source of factual recommendations. 

## **31. STEP 15 — Implement Private Farm Memory** 

Use SQLite. 

Minimum tables: 

farm 

observations 

diagnoses advisories livestock Every analysis should save: 

timestamp farm_id 

domain 

image prediction confidence 

text 

final advisory 

route 

Then the next cloud query can retrieve: 

Previous diagnoses Previous treatments 

Previous advisories 

## **32. This is where your prototype becomes more than "Plant Disease Classifier"** 

Suppose: 

## **First visit** 

10 Aug Tomato Early Blight Treatment advised 

## **Second visit** 

15 Aug New image Your system says: "A similar early-blight issue was recorded on this farm 5 days ago." That demonstrates **Private Farm Memory** . This is worth much more than adding another fancy AI model. 

## **33. STEP 16 — Build the Streamlit application** 

Only after backend functions work. 

Main UI: 

🐄 Unified AI Agri-Vision 

Farm: Demo Farm 

Status: 🟢 Offline AI Ready Then: 

Choose input 

[ 📷 Crop ] [ 🐄 Livestock ] [ 🎙 Voice ] 

## **34. Crop UI** 

Upload Crop Image 

↓ 

Voice description (optional) 

- ↓ 

- [ ANALYZE ] 

Result: 

- 🐄 Crop Expert Activated 

Prediction: 

Tomato Early Blight 

Confidence: 

93% 

Evidence: 

✓ Image 

- ✓ Farmer description 

Decision: 

- 🟢 High confidence 

- → Local processing 

Recommended action: 

... 

## **35. Cloud escalation UI** 

For a low-confidence image: 

- ⚠ Local AI Confidence: 54% 

The system detected conflicting evidence. 

Cloud escalation initiated... 

- ✓ Image sent 

- ✓ Farmer description included 

- ✓ Farm context included 

- ✓ Trusted knowledge retrieved 

Generating advisory... 

Then: 

- ☁ Expert Advisory 

Possible condition: 

... 

Recommended action: 

... 

When to seek expert: 

... 

This is a fantastic demonstration of your architecture. 

## **36. Livestock UI** 

Show: 

- 🐄 Livestock Monitoring 

Animal ID: COW-017 

Image 

[Upload] 

Sensor data 

Temperature    39.8°C 

Activity       Low Feed intake    Low 

[ ANALYZE ] Then: Livestock Expert 

↓ 

Image evidence 

+ 

Sensor evidence 

↓ 

Fusion 

↓ 

Confidence 

## **37. Voice UI** 

This should be your most visually impressive flow. 

🎙 Speak to your farm assistant 

[ 🐄 Record ] 

Hindi: 

" पर " टमा�टर की� पत्ति�यों� भू�र� धब्बे� हैं�। 

Then: 

- ✓ Voice processed locally 

- ✓ Hindi transcription complete 

- ✓ No cloud required for transcription 

Then: 

Image + Text 

↓ 

Local expert 

↓ 

Fusion 

That directly proves your offline-first claim. 

## **38. STEP 17 — Add a visible offline/cloud indicator** 

This is important. 

At the top of the application: 

- 🟢 LOCAL MODE 

when everything is local. 

For escalation: 

- 🟡 CLOUD ASSIST 

This lets the judge visually understand your core innovation. 

## **39. STEP 18 — Add a "Why did we escalate?" explanation** 

For low confidence: 

Why cloud? 

- Local confidence: 52% 

- Text and image evidence conflict 

- Additional contextual reasoning required 

This makes your system appear **deliberate rather than randomly API-driven** . 

## **40. STEP 19 — Make the cloud prompt strict** 

Your Gemini prompt should essentially say: 

You are an agricultural advisory engine. 

Use: 

1. Current image analysis 

2. Farmer's text 

3. Sensor evidence 

4. Farm history 

5. Retrieved trusted knowledge 

Rules: 

- Do not invent diagnoses. 

- Do not invent pesticide/veterinary dosage. 

- Distinguish possible diagnosis from confirmed diagnosis. 

- If evidence is insufficient, say so. 

- Recommend professional consultation when appropriate. 

- Give concise actionable recommendations. 

- Return structured JSON. 

This will make the output considerably safer. 

## **41. STEP 20 — Add an explicit prototype limitation** 

Do not claim: 

"The system accurately diagnoses all diseases." 

Instead: 

**Prototype supports selected crop diseases and livestock conditions using pretrained specialist models.** 

And: 

## **Low-confidence or conflicting cases are escalated to the cloud advisory engine.** 

That's a much stronger engineering position. 

## **42. Final complete execution pipeline** 

Your code should ultimately execute: 

USER │ ┌──────────┼──────────┐ ↓          ↓          ↓ Image      Voice      Sensor │          │          │ │      IndicConformer │ │          ↓          │ │         Text        │ │          │          │ 

↓          ↓          ↓ 

Specialist Evidence Extraction 

│          │          │ ↓          ↓          ↓ Visual     Text        Sensor Expert    Evidence     Rules │          │          │ └──────────┼──────────┘ ↓ Late Fusion ↓ Confidence + Safety ↓ ┌──────┴──────┐ ↓             ↓ HIGH           LOW ↓             ↓ Local Advisory   Cloud │             ↓ │       Gemini + RAG │             + │       Farm Context │             ↓ └──────→ Advisory ↓ TTS ↓ Farmer ↓ Farm Memory 

## **43. What you should NOT implement** 

Given your constraints, explicitly put these out of scope: 

## **❌ Federated learning** 

Already decided. 

## **❌ Learned multimodal fusion** 

Use rule-based late fusion. 

## **❌ Training crop model** 

Use pretrained. 

## **❌ Training livestock model** 

Use pretrained. 

## **❌ Local LLM** 

Not necessary. 

## **❌ Local VLM** 

Not necessary. 

## **❌ Automatic task classifier** 

Use UI/metadata for prototype. 

## **❌ Physical IoT integration** 

Simulate sensor data unless hardware already works. 

## **❌ Large RAG infrastructure** 

Use a small local vector index. 

## **44. What should be genuinely "offline" in your demo?** 

This distinction matters. 

## **Completely local** 

📷 Image preprocessing 

↓ 

Crop/Livestock specialist 

↓ 

🎙 Hindi ASR 

↓ 

Text evidence extraction 

↓ 

Sensor processing 

↓ 

Fusion 

↓ 

Confidence gate 

↓ 

High-confidence advisory 

↓ 

Hindi TTS 

## **Cloud only when necessary** 

Low confidence 

↓ 

Cloud ↓ Gemini + 

RAG + 

Farm context 

↓ 

Advisory 

That is a **true offline-first architecture** . 

## **45. TTS decision I would make right now** 

## **First attempt** 

## **AI4Bharat Hindi FastPitch + HiFi-GAN** 

Reason: 

- Hindi-specific 

- AI4Bharat 

- pretrained 

- local 

- established TTS architecture 

- repository provides Hindi checkpoints/inference path. (GitHub) 

## **If setup becomes painful** 

Try **IndicF5** . It supports Hindi and has a modern inference path, but is larger. (Hugging Face) 

## **If you want the best-quality demo and have GPU** 

Try **Indic Parler-TTS** , but only after everything else works; its current checkpoint is ~3.75 GB and gated, making it a poor critical-path dependency. (Hugging Face) 

## **If you need a very lightweight experimental option** 

Investigate the community vani-tts ONNX Hindi project, but verify license/reliability before using it in the submitted prototype. (GitHub) 

## **46. Recommended development order** 

This is the **exact order I would follow** , because each step creates a usable checkpoint: 

1. Project skeleton 

↓ 

2. Crop model inference 

- ↓ 

3. Livestock model inference 

↓ 

4. Hindi IndicConformer ASR 

↓ 

5. Text evidence extraction 

↓ 

6. Sensor rules 

↓ 

7. Late fusion 

↓ 

8. Confidence gate 

↓ 

9. Local advisory 

↓ 

## 10. Hindi TTS 

↓ 

11. SQLite farm memory 

↓ 

## 12. Gemini cloud escalation 

↓ 

## 13. RAG 

- ↓ 

14. Streamlit integration 

- ↓ 

15. End-to-end testing 

↓ 

16. UI polishing 

↓ 

17. Demo rehearsal 

## **Do not reverse this order.** 

In particular, don't start with Streamlit, RAG or Gemini. 

## **47. Time budget separately** 

Since you asked to keep time details separate from the main plan, here is the recommended **15-hour budget** . 

**Time Target** 

- **0–0.5 h** Repo + environment + dependencies 

- **0.5–1.5 h** Crop + livestock pretrained models working 

- **1.5–3 h** IndicConformer Hindi ASR 

- **3–4 h** Hindi text evidence extraction 

- **4–5 h** Sensor simulation + anomaly rules 

- **5–6 h** Late fusion + confidence gate 

- **6–7 h** Local actionable advisory 

- **7–8 h** Hindi TTS 

- **8–9 h** SQLite farm memory 

- **9–10.5 h** Gemini cloud escalation 

- **10.5–11.5 h** RAG knowledge base 

- **11.5–13 h** Streamlit integration 

- **13–14 h** End-to-end debugging + demo cases 

## **Time Target** 

**14–15 h** UI polish + demo rehearsal 

## **But use these as checkpoints, not rigid deadlines.** 

The critical milestones are: 

## **Hour 3** 

Image → prediction 

Voice → Hindi text 

## **Hour 6** 

Image + text + sensor 

→ fusion 

→ confidence 

## **Hour 9** 

High confidence 

→ fully local advisory + TTS 

## **Hour 11.5** 

Low confidence 

→ Gemini + RAG + farm context 

## **Hour 13** 

Everything inside Streamlit 

## **Hour 15** 

**Stop coding.** 

## **48. One final recommendation about the TTS requirement** 

I would **not put "AI4Bharat IndicConformer Hindi TTS" in your documentation** , because that is technically incorrect. 

Write: 

## **Offline Hindi ASR: AI4Bharat IndicConformer (30M) Offline Hindi TTS: AI4Bharat Hindi FastPitch + HiFi-GAN / IndicF5** 

AI4Bharat's own model catalogue separates IndicConformer as ASR from IndicF5/Indic Parler-TTS as TTS. (Hugging Face) 

And your final architecture label can simply be: 

## **Offline Hindi Speech I/O** 

with the technical implementation specified on the technical slide. 

## **The most important implementation principle** 

Don't try to make the prototype _look_ like a giant AI system by adding models. 

Make the **decision flow** real: 

## **Voice → local Hindi ASR → text evidence** 

**Image → local specialist Sensor → local evidence Evidence → fusion → confidence High confidence → completely local advisory Low confidence → cloud + RAG + farm memory Advisory → Hindi speech** 

If that entire loop works reliably, you have a genuinely convincing prototype of your proposed architecture rather than just a collection of disconnected AI demos. 

