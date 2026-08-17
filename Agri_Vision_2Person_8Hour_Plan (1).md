# 2-Person / 8-Hour Build Plan 

### **Unified AI Agri-Vision Platform — End-to-End Prototype** 

_Two people working fully in parallel, with AI coding agents, to a single integrated demo in 8 hours_ 

## **0. How the Architecture Diagram Maps to This Plan** 

Your diagram has 3 zones. This plan assigns each zone to a person so both can code simultaneously without blocking each other: 

|**Diagram Zone**|**Contents**|**Owner in this plan**|
|---|---|---|
|Zone 1 — Farmer's Phone<br>(Edge)|Capture+Quality Check, Task Router, MoE Specialist<br>Experts (Crop/Livestock), Confdence & Safety Gate,<br>On-Device Advisory Output|PERSON A|
|Zone 2 — Cloud Advisory Layer|Cloud Gateway, RAG Engine (Trusted KB + Retrieval<br>+ Farm Context), Actonable Advisory, Farmer-<br>Ready Output|PERSON B|
|Zone 3 — Farm Memory &<br>Learning|Private Farm Memory (Farm Records Store), My<br>Farm History Timeline|PERSON B (owns DB; both<br>write to it)|
|Voice path<br>(Photo/Voice/Sensor input,<br>cross-cutng)|Hindi ASR → text evidence → fed into Task Router /<br>fusion|PERSON B builds ASR+TTS;<br>PERSON A consumes the<br>text evidence output|



_Why this split: Person A owns everything that must run fully offline on-device (Zone 1 — vision models, sensor rules, fusion, confidence gate). Person B owns everything that talks to the outside world or persists data (Zone 2 cloud/RAG, Zone 3 memory, plus Hindi speech I/O, which is model-heavy but independent of the vision models). Neither person's core work blocks the other's, as long as the JSON data contract (Section 2) is frozen first._ 

## **1. Tech Stack — Frozen From the Doc (Do Not Deviate)** 

|**Component**|**Exact choice (from your doc)**|**Hugging Face / source**<br>**reference**|
|---|---|---|
|UI|Streamlit||
|Backend|Python / FastAPI||
|Crop specialist|Pretrained PlantVillage MobileNetV3|search HF for a PlantVillage-<br>fnetuned MobileNetV3<br>checkpoint, e.g. models tagged<br>'plant-disease mobilenetv3'|
|Livestock specialist|Pretrained catle-disease model (EfcientNet-B3 class)|search HF for 'catle disease<br>classifcaton efcientnet'|
|ASR (Hindi, ofine)|AI4Bharat IndicConformer — Hindi, ~30M params,<br>built for real-tme on-device Indian-language ASR|huggingface.co/collectons/<br>ai4bharat/indicconformer|
|Text evidence|Rule-based symptom extractor (no model)|hand-writen dictonary — no<br>HF model needed|
|Sensor|Simulated values + threshold rules (no model)|hand-writen — no HF model<br>needed|
|Fusion|Rule/score-based late fusion (no model)|hand-writen logic — no HF<br>model needed|



|**Component**|**Exact choice (from your doc)**|**Hugging Face / source**<br>**reference**|
|---|---|---|
|Confdence gate|Threshold + modality agreement (no model)|hand-writen logic — no HF<br>model needed|
|Local advisory|Local JSON knowledge mapping (no model)|hand-writen<br>knowledge/local_advisories.json|
|Cloud LLM|Gemini API||
|RAG|FAISS or Chroma + small curated knowledge base||
|Farm memory|SQLite||
|Hindi TTS (primary)|AI4Bharat Hindi FastPitch + HiFi-GAN|github.com/AI4Bharat/Indic-TTS|
|Hindi TTS (fallback)|IndicF5 (~0.4B params, Hindi + 10 other languages,<br>MIT licensed)|huggingface.co/ai4bharat/<br>IndicF5|
|Hindi TTS (stretch, GPU<br>only)|Indic Parler-TTS (~3.75GB, gated) — do not use unless<br>everything else already works|huggingface.co/ai4bharat/indic-<br>parler-ts|
|Privacy-preserving<br>learning|Not implemented (explicitly out of scope)||



**Important correction carried over from the doc: IndicConformer is ASR only, not TTS. Never label it as Hindi TTS in your slides — ASR and TTS are two separate AI4Bharat models.** 

## **2. The Shared Data Contract — Freeze This Before Writing Any Code (Minute 0–15)** 

Both people must agree on this JSON shape together, in the first 15 minutes, before splitting up. This is the only thing that makes true parallel work possible. 

##### **Image expert output (Person A):** 

- {"domain":"crop"|"livestock", "input_type":"image", "prediction": str, "confidence": float, "top_k": [[label, prob], ...]} 

##### **ASR output (Person B):** 

- {"text": str, "language":"hi", "confidence": null} 

##### **Text evidence output (Person A, consumes Person B\'s ASR text):** 

- {"symptoms": [str,...], "crop": str, "severity_hint": str} 

##### **Sensor output (Person A):** 

- {"domain":"livestock", "temperature": float, "activity": str, "feed_intake": str, "anomaly": bool} 

- **Fusion output (Person A, this is what Person B\'s cloud call and UI consume):** 

   - {"prediction": str, "visual_confidence": float, "text_support": bool, "sensor_support": bool|null, "evidence_agreement": "high"|"medium"|"low", "final_confidence": float, "route": "local"|"cloud"} 

##### **Cloud request payload (Person B builds this from Person A\'s fusion output):** 

- {"domain": str, "image_prediction": str, "visual_confidence": float, "farmer_text": str, "text_evidence": [str,...], "sensor_data": obj|null, "farm_history": str, "retrieved_knowledge": str} 

_Agree on this literally by pasting it into a shared file (contract.md) at minute 15. Do not change a shape later without telling the other person._ 

## **3. PERSON A — Edge / Vision / Fusion Track (Zone 1)** 

Owns: crop expert, livestock expert, sensor expert, text-evidence consumption, task router, fusion, confidence gate, local advisory. Everything that must work fully offline. 

#### **Hour-by-Hour Plan — Person A** 

|**Time**|**Task**|**How to implement**|**Model /**<br>**reference**|
|---|---|---|---|
|0:00–<br>0:15|Agree data contract<br>with Person B; set up<br>repo skeleton<br>(experts/, multmodal/,<br>knowledge/,<br>demo_data/)|Shared step — see Secton 2||
|0:15–<br>1:15|Crop specialist: image<br>→ MobileNetV3 →<br>sofmax → top-3|Download a PlantVillage-pretrained MobileNetV3 checkpoint<br>from Hugging Face (search 'plant disease mobilenetv3' or<br>'plantvillage'). Load with transformers/tmm, run inference<br>on demo_data/crop images, wrap output in the contract<br>JSON. Use an AI coding agent (Claude Code / Cursor) with<br>the prompt: 'write crop_expert.py that loads a HF image<br>classifer, preprocesses a PIL image, returns top-3 as the<br>JSON contract below' — paste the contract.|PlantVillage<br>MobileNetV3<br>(HF)|
|1:15–<br>2:00|Livestock specialist:<br>same interface,<br>diferent model|Same patern as crop — fnd a catle-disease HF checkpoint<br>(or if unavailable in tme, use a general animal-health image<br>classifer and clearly relabel classes in local_advisories.json).<br>Keep it image-only, same contract shape.|Catle-disease<br>EfcientNet-B3<br>class (HF)|
|2:00–<br>2:30|INTEGRATION<br>CHECKPOINT 1 — sync<br>with Person B: confrm<br>ASR text-evidence<br>format matches<br>contract|Quick call/message — verify shapes match exactly||
|2:30–<br>3:15|Text evidence<br>extractor (rule-based,<br>no model)|Write multmodal/text_evidence.py with a Hindi + English<br>keyword dictonary (<br>→<br>भरधबब<br>brown_spots,<br>प�ल�<br>→<br>पत�य�<br>yellow_leaves,<br>→<br>सफदप�उडर<br>white_powder,<br>पत�य�<br>→<br>मड<br>leaf_curl,<br>→<br>क�ड<br>insects,<br>→<br>मरझ�<br>wiltng). Have the<br>coding agent generate the dict scafolding, you fll in domain<br>terms. Deterministc string matching only — no model.||
|3:15–<br>3:45|Sensor expert<br>(simulated)|Hard-code a demo sensor panel (temperature, actvity%,<br>feed_intake%) + threshold rules → alerts + anomaly bool. No<br>model needed — a dict + if-statements.||
|3:45–<br>4:15|Task router|Explicit UI-driven selecton (Crop / Livestock butons) — not<br>a learned classifer. Just a functon that dispatches to the<br>right expert based on a passed-in domain string. Stll print<br>'Detected task → Expert selected' for the demo.||
|4:15–<br>5:15|Late evidence fusion<br>(multmodal/fusion.py)<br>— the key new<br>component|score = visual_confdence; if text supports → +0.10; if text<br>conficts → -0.20; cap at 0.99. Do not let text arbitrarily<br>override image. Output the full fusion JSON from Secton 2.<br>Ask the coding agent: 'implement this exact rule-based<br>fusion logic returning this exact JSON shape' and hand it the<br>contract + these rules verbatm.||
|5:15–|Confdence & safety|3 inputs: model confdence, evidence agreement, input||



|**Time**|**Task**|**How to implement**|**Model /**<br>**reference**|
|---|---|---|---|
|5:45|gate|quality. HIGH = confdence≥threshold(e.g. 0.75) AND<br>evidence consistent AND quality OK → route='local'. Else →<br>route='cloud'.||
|5:45–<br>6:15|Local advisory|knowledge/local_advisories.json keyed by conditon name:<br>{summary, actons[], warning}. Write 6–10 entries (tomato<br>early/late blight, potato blight, maize rust, lumpy skin<br>disease, FMD, abnormal temp). High-confdence path<br>returns this directly — fully ofine.||
|6:15–<br>6:45|INTEGRATION<br>CHECKPOINT 2 — hand<br>fusion+confdence<br>output to Person B for<br>their cloud escalaton<br>call and UI|||
|6:45–<br>7:30|Wire Person A's whole<br>pipeline into Streamlit<br>tabs (Crop, Livestock)<br>alongside Person B's<br>shell|Person B owns the Streamlit shell; Person A plugs expert<br>calls into it||
|7:30–<br>8:00|End-to-end test with<br>Person B: 4 fxed Hindi<br>sentences, confrm 2<br>route local / 1–2 route<br>cloud|||



## **4. PERSON B — Voice / Cloud / RAG / Memory Track (Zone 2 + 3)** 

Owns: Hindi ASR, Hindi TTS, Gemini cloud escalation, RAG knowledge base, SQLite farm memory, and the Streamlit UI shell. Everything that talks to the outside world or persists data. 

#### **Hour-by-Hour Plan — Person B** 

|**Time**|**Task**|**How to implement**|**Model /**<br>**reference**|
|---|---|---|---|
|0:00–<br>0:15|Agree data contract<br>with Person A (same<br>session, see Secton<br>2)|||
|0:15–<br>1:30|Hindi ASR —<br>standalone test frst|Pull AI4Bharat IndicConformer Hindi (~30M) from the HF<br>collecton. Write test_asr.py: load model → run on<br>demo_data/audio/*.wav (record 3–4 fxed Hindi sentences<br>yourself frst: crop / livestock / healthy / ambiguous) → print<br>transcript. Prove load tme, inference tme, and transcript<br>quality BEFORE wiring into anything else. Use an agent: 'write<br>a script that loads AI4Bharat IndicConformer Hindi from<br>Hugging Face and transcribes a wav fle, return {text,<br>language, confdence} JSON'.|AI4Bharat<br>IndicConformer<br>(HF collecton:<br>ai4bharat/indic<br>conformer)|
|1:30–<br>2:00|Wrap ASR as a<br>functon returning the<br>contract JSON; hand<br>text output format to|||



|**Time**|**Task**|**How to implement**|**Model /**<br>**reference**|
|---|---|---|---|
||Person A|||
|2:00–<br>2:30|INTEGRATION<br>CHECKPOINT 1 —<br>confrm ASR JSON<br>shape with Person A<br>(same as their entry)|||
|2:30–<br>3:30|Hindi TTS — primary<br>path|Try AI4Bharat Hindi FastPitch + HiFi-GAN frst<br>(github.com/AI4Bharat/Indic-TTS — clone repo, use provided<br>Hindi checkpoint + inference script). If setup stalls past ~45<br>min, fall back immediately to IndicF5<br>(huggingface.co/ai4bharat/IndicF5, simpler HF pipeline call).<br>Do not atempt Indic Parler-TTS — it's 3.75GB and gated,<br>wrong for an 8-hour budget.|AI4Bharat<br>FastPitch+HiFi-<br>GAN → fallback<br>IndicF5|
|3:30–<br>4:15|SQLite farm memory<br>schema + functons|Tables: farm, observatons, diagnoses, advisories, livestock.<br>Write save_observaton() and get_farm_history(farm_id)<br>functons. Every analysis run should insert a row;<br>get_farm_history returns prior diagnoses as a string for cloud<br>context. Ask the agent to scafold the schema + CRUD<br>functons from this table list.||
|4:15–<br>5:15|RAG knowledge base|Write 8–10 short knowledge entries as .md or .json (Conditon<br>/ Symptoms / Visual indicators / Recommended actons /<br>Preventon / When to seek expert / Source) covering: tomato<br>early/late blight, potato early/late blight, maize rust, maize<br>leaf blight, lumpy skin disease, FMD, abnormal<br>temperature/actvity. Embed with a small sentence-<br>transformer and index with FAISS or Chroma (both pip-<br>installable, no HF auth needed for the embedding model, e.g.<br>'sentence-transformers/all-MiniLM-L6-v2' from HF).|sentence-<br>transformers/<br>all-MiniLM-L6-<br>v2 (HF) +<br>FAISS/Chroma|
|5:15–<br>6:15|Gemini cloud<br>escalaton + strict<br>prompt|gemini_client.py: takes the cloud request payload (Secton 2)<br>+ RAG-retrieved snippets, sends a strict system prompt: use<br>image+text+sensor+farm history+retrieved knowledge; never<br>invent diagnoses/dosages; distnguish possible vs confrmed;<br>say so if evidence insufcient; recommend expert<br>consultaton when appropriate; return structured JSON. Ask<br>the agent to draf this prompt string then you tghten the<br>safety rules.||
|6:15–<br>6:45|INTEGRATION<br>CHECKPOINT 2 —<br>receive Person A's<br>fusion/confdence<br>output, wire the local-<br>vs-cloud branch, call<br>Gemini only when<br>route='cloud'|||
|6:45–<br>7:30|Streamlit UI shell +<br>wiring both people's<br>pipelines together|3 tabs (Crop, Livestock, Voice); top banner<br>LOCAL<br>🟢<br>MODE /<br>CLOUD ASSIST; 'Why cloud?' panel showing<br>🟡<br>confdence % + evidence confict; call Person A's fusion+gate,<br>branch to local_advisories.json or Gemini+RAG, then call your<br>TTS on the fnal advisory text.||
|7:30–<br>8:00|End-to-end test<br>together: 4 fxed<br>Hindi sentences|||



|**Time**|**Task**|**How to implement**|**Model /**<br>**reference**|
|---|---|---|---|
||through full pipeline;<br>confrm memory<br>persists and second<br>run shows farm<br>history recall|||



## **5. Using AI Coding Agents to Hit 8 Hours** 

Both people should run a coding agent (Claude Code, Cursor, or similar) locally the entire session, not just for isolated snippets. Concretely: 

- Paste the full data contract (Section 2) into the agent's context once at the start of your track so every generated function already returns the right shape. 

- For each HF model integration, give the agent the exact model name/collection and ask it to write the load+preprocess+infer+format function in one shot, then you just run and debug — don't hand-write boilerplate. 

- For rule-based components (fusion, confidence gate, sensor rules, text evidence), give the agent the exact logic described in this plan and your contract shapes — these are small enough that agent-generated code should need only minor edits. 

- Use the agent to generate synthetic test fixtures (mock fusion JSON, mock ASR output) so each person can build against realistic data before the other person's real component is ready. 

- Keep prompts scoped to one function/file at a time — asking an agent for 'the whole app' produces code neither of you can quickly debug under a time limit. 

## **6. Integration Timeline Summary (Both People)** 

|**Checkpoint**|**Time**|**What's proven**|
|---|---|---|
|Contract freeze|0:00–0:15|Both agree on every JSON shape before writng model code|
|Checkpoint 1|2:00–2:30|Person A's experts return contract JSON; Person B's ASR returns contract<br>JSON|
|Checkpoint 2|6:15–6:45|Person A's fusion+confdence output correctly drives Person B's local-vs-<br>cloud branch|
|UI wiring|6:45–7:30|Both pipelines run inside one Streamlit app with the ofine/cloud<br>banner|
|Final test|7:30–8:00|4 fxed Hindi sentences run end-to-end; 2 stay local, 1–2 escalate to<br>cloud; farm memory recalls a prior visit|



## **7. What to Explicitly Skip in 8 Hours** 

- Federated / privacy-preserving learning — not implemented. 

- Learned multimodal fusion or a learned task router — rule-based / UI selection only. 

- Training any model — pretrained checkpoints only. 

- Physical IoT hardware — simulated sensor data only. 

- Indic Parler-TTS — too large/gated for this budget; FastPitch+HiFi-GAN → IndicF5 fallback only. 

- A large RAG corpus — 8–10 curated entries is enough to prove the mechanism. 

## **8. Final Demo Script (What the Judges See)** 

1. Speak a Hindi sentence → 🟢 'Voice processed locally, no cloud required for transcription' → transcript shown. 

2. Upload a matching crop image → expert activated → fusion combines image+text → confidence shown → HIGH → 🟢 LOCAL DECISION card with advisory, entirely offline. 

3. Upload an ambiguous/low-confidence case → 🟡 CLOUD ESCALATION card → 'Why cloud?' panel explains conflicting evidence → Gemini+RAG advisory returned with farm-history reference. 

4. Re-run a similar case → system says 'a similar issue was recorded on this farm N days ago' — proving Private Farm Memory. 

