"""
streamlit_app.py — Person B, Zone shell

3 tabs (Crop, Livestock, Voice).
Wires Person A's Zone 1 pipeline + Person B's Zone 2/3 modules together.
"""

from __future__ import annotations

import sys
import json
from pathlib import Path
import os
import tempfile
from dotenv import load_dotenv

# Load environment variables from .env file before anything else
load_dotenv()

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import streamlit as st

from src.zone1_edge.pipeline import run_zone1_pipeline, build_cloud_payload_stub
from src.zone1_edge.speech import hindi_asr, hindi_tts
from src.zone2_cloud.gemini import gemini_client
from src.zone2_cloud.rag import retriever
from src.zone3_memory.db import farm_memory
from src.zone3_memory.db import auth

st.set_page_config(page_title="Agri-Vision Platform", layout="wide", page_icon="🌾")

# Inject Custom CSS for professional look and animations
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
html, body, [class*="css"]  {
    font-family: 'Inter', sans-serif;
}
.stButton > button {
    background: linear-gradient(135deg, #2ecc71 0%, #27ae60 100%);
    color: white;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    transition: all 0.3s ease;
    box-shadow: 0 4px 6px rgba(46, 204, 113, 0.2);
}
.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 12px rgba(46, 204, 113, 0.3);
    color: white;
}
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}
.result-box {
    animation: fadeIn 0.5s ease-out forwards;
    padding: 1.5rem;
    border-radius: 12px;
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    margin-top: 1rem;
    margin-bottom: 1rem;
}
.cloud-box {
    background: #fffbeb;
    border-color: #fde68a;
}
.local-box {
    background: #f0fdf4;
    border-color: #bbf7d0;
}
/* Translate internal Streamlit File Uploader text */
div[data-testid="stFileUploaderDropzoneInstructions"] > div > span {
    display: none;
}
div[data-testid="stFileUploaderDropzoneInstructions"] > div::before {
    content: "Drag and drop file here / फ़ाइल यहाँ खींचें और छोड़ें";
    visibility: visible;
    display: block;
    margin-bottom: 5px;
}
div[data-testid="stFileUploaderDropzoneInstructions"] > div small {
    display: none;
}
div[data-testid="stFileUploaderDropzoneInstructions"] > div::after {
    content: "Limit 200MB per file • JPG, JPEG, PNG / सीमा 200MB प्रति फ़ाइल";
    visibility: visible;
    display: block;
    font-size: 0.8em;
    color: #666;
}
</style>
""", unsafe_allow_html=True)

st.title("🚜 Agri-Vision: The Fully Unified Crop & Livestock Platform")
st.markdown("#### *One Login. One History. Total Farm Management. / एक लॉगिन. एक इतिहास. संपूर्ण खेत प्रबंधन.*")
st.caption("Crop Disease ID / फ़सल रोग पहचान + Livestock Monitoring / पशुधन निगरानी + Historical Records / ऐतिहासिक रिकॉर्ड — Offline-First / ऑफ़लाइन-प्रथम")
st.divider()

# Ensure DB is initialized
farm_memory.init_db()

# Session State for Auth
if "farmer_id" not in st.session_state:
    st.session_state.farmer_id = None
if "farmer_text_from_voice" not in st.session_state:
    st.session_state.farmer_text_from_voice = ""

def render_login():
    st.subheader("Farmer Login / Signup / किसान लॉगिन / साइनअप")
    tab1, tab2 = st.tabs(["Login / लॉगिन", "Signup / साइनअप"])
    
    with tab1:
        phone_login = st.text_input("Phone Number / फ़ोन नंबर", key="login_phone")
        pin_login = st.text_input("PIN / पिन", type="password", key="login_pin")
        if st.button("Login / लॉगिन"):
            fid = auth.login(phone_login, pin_login)
            if fid:
                st.session_state.farmer_id = fid
                st.success("Logged in successfully!")
                st.rerun()
            else:
                st.error("Invalid phone or PIN.")
                
    with tab2:
        name_signup = st.text_input("Full Name / पूरा नाम", key="signup_name")
        phone_signup = st.text_input("Phone Number / फ़ोन नंबर", key="signup_phone")
        pin_signup = st.text_input("Create PIN / पिन बनाएं", type="password", key="signup_pin")
        if st.button("Signup / साइनअप"):
            try:
                fid = auth.signup(phone_signup, pin_signup, name_signup)
                st.session_state.farmer_id = fid
                st.success("Account created successfully!")
                st.rerun()
            except ValueError as e:
                st.error(str(e))

if not st.session_state.farmer_id:
    render_login()
    st.stop()

# If logged in:
FARM_ID = st.session_state.farmer_id
FARMER_NAME = auth.get_farmer_name(FARM_ID)
EXPERT_MODE = os.environ.get("AGRIVISION_EXPERT_MODE", "mock")

with st.sidebar:
    st.write(f"👨‍🌾 **Logged in as:** {FARMER_NAME}")
    st.caption(f"ID: {FARM_ID}")
    st.caption(f"Mode: {EXPERT_MODE}")
    if st.button("Logout / लॉग आउट"):
        st.session_state.farmer_id = None
        st.rerun()

tab_auto, tab_history = st.tabs(["⚡ Auto-Detect / स्वतः पहचान", "📖 Farm History / खेत का इतिहास"])

def process_pipeline_result(result, farmer_text):
    gate = result["gate"]
    
    # Zone 3: Save Observation
    obs_id = farm_memory.save_observation(
        farm_id=FARM_ID,
        domain=result.get("image_output", {}).get("domain", "unknown"),
        image_prediction=gate.get("prediction", "unknown"),
        visual_confidence=gate.get("visual_confidence", 0.0),
        farmer_text=farmer_text or "",
        sensor_json=json.dumps(result.get("sensor_output") or {}),
        route=gate.get("route", "local")
    )
    
    if gate.get("route") == "reject":
        st.error(f"❌ {gate.get('reason', 'Image too blurry or dark. Please retake the photo.')}")
        st.button("Retake Photo / फिर से फ़ोटो लें", on_click=lambda: st.experimental_rerun() if hasattr(st, "experimental_rerun") else st.rerun())
        return None

    quality_flag = result.get("quality", {}).get("quality_flag", "ok")
    if quality_flag == "warn":
        st.warning("⚠️ Image quality is low (blurry/dark). Predictions may be less accurate.")

    if gate.get("route") == "local":
        clean_pred = gate.get("prediction", "Unknown").replace("___", " ").replace("_", " ")
        
        # Zone 1: Offline Advisory
        adv = result.get("local_advisory", {}) or {}
        
        # Zone 3: Save Diagnosis and Advisory
        diag_id = farm_memory.save_diagnosis(
            obs_id, 
            condition=gate.get("prediction", "Unknown"), 
            certainty="possible", 
            final_confidence=gate.get("final_confidence", 0.0)
        )
        farm_memory.save_advisory(
            diag_id, 
            source="local_offline", 
            summary=adv.get("summary", ""), 
            actions=adv.get("actions", []), 
            warning=adv.get("warning", "")
        )
        
        st.markdown(f'''
        <div class="result-box local-box">
            <h3 style="margin-top:0;">🟢 Local AI Decision: {clean_pred}</h3>
            <p><strong>Confidence:</strong> {gate.get('final_confidence', 0.0):.0%}</p>
            <p><strong>Summary:</strong> {adv.get('summary', '')}</p>
        </div>
        ''', unsafe_allow_html=True)
        
        for a in adv.get("actions", []):
            st.write(f"- {a}")
            
        if adv.get("warning") and adv.get("warning") != "None — recheck if new symptoms appear.":
            st.warning(adv.get("warning"))
            
        if "explainability" in result:
            st.markdown("### 🔍 AI Reasoning & Confidence Details / एआई तर्क और विश्वास विवरण")
            expl = result["explainability"]
            st.write("**Top Predictions:**")
            for rank, data in expl.get("top3", {}).items():
                st.write(f"- {data['label']}: {data['confidence']:.0%}")
            st.write(f"**Routing Reason:** {expl.get('reason_string', '')}")
            
        return adv.get("summary", "")
    else:
        st.warning(f"🟡 CLOUD ASSIST needed — Low confidence or complex anomaly detected. Escaling to Gemini via Satellite/Cloud...")
        
        if "explainability" in result:
            st.markdown("### 🔍 AI Reasoning for Escalation / एस्केलेशन के लिए एआई तर्क")
            expl = result["explainability"]
            st.write("**Top Local Predictions (Too low to trust):**")
            for rank, data in expl.get("top3", {}).items():
                st.write(f"- {data['label']}: {data['confidence']:.0%}")
            st.write(f"**Evidence Agreement:** {gate.get('evidence_agreement', 'unknown')}")
            st.write(f"**Routing Reason:** {expl.get('reason_string', '')}")
        
        with st.container():
            st.write("### ☁️ Processing Cloud Diagnostic... / क्लाउड डायग्नोस्टिक प्रोसेस हो रहा है...")
            with st.spinner("Processing..."):
                st.write("1. Retrieving localized farming knowledge (RAG)...")
                query = f"{gate.get('prediction', '')} {farmer_text or ''}"
                rag_knowledge = retriever.retrieve(query)
            
                st.write("2. Fetching historical farm health records...")
                farm_hist = farm_memory.get_farm_history(FARM_ID)
            
                st.write("3. Packaging sensor data and visual embeddings...")
                payload = build_cloud_payload_stub(result)
                payload["farmer_text"] = farmer_text or ""
                payload["farm_history"] = farm_hist
                payload["retrieved_knowledge"] = rag_knowledge
            
                st.write("4. Consulting Gemini Agronomy Expert...")
                cloud_result = gemini_client.call_gemini(payload)
            st.success("Cloud Diagnostic Complete! / क्लाउड डायग्नोस्टिक पूरा हुआ!")
            
            diag = cloud_result.get("diagnosis", {})
            adv = cloud_result.get("advisory", {})
            
            # Zone 3: Save Cloud Diagnosis and Advisory
            diag_id = farm_memory.save_diagnosis(
                obs_id, 
                condition=diag.get("condition", "Unknown"), 
                certainty=diag.get("certainty", "possible"), 
                final_confidence=gate.get("final_confidence", 0.0)
            )
            farm_memory.save_advisory(
                diag_id, 
                source="cloud_gemini", 
                summary=adv.get("summary", ""), 
                actions=adv.get("actions", []), 
                warning=adv.get("warning", "")
            )
            
            st.markdown(f'''
            <div class="result-box cloud-box">
                <h3 style="margin-top:0;">☁️ Cloud Expert Diagnosis</h3>
                <p><strong>Condition:</strong> {diag.get('condition', 'Unknown')} ({diag.get('certainty', 'possible')})</p>
                <p><strong>Summary:</strong> {adv.get('summary', '')}</p>
            </div>
            ''', unsafe_allow_html=True)
            
            for a in adv.get("actions", []):
                st.write(f"- {a}")
                
            if adv.get("warning"):
                st.warning(adv.get("warning"))
                
            if cloud_result.get("expert_consultation_recommended"):
                st.error("🚨 **CRITICAL:** Expert consultation strongly recommended immediately!")
                
            if cloud_result.get("cited_knowledge"):
                st.markdown("### 📚 RAG Citations (Knowledge Base) / ज्ञानकोष संदर्भ")
                for k in cloud_result.get("cited_knowledge", []):
                    st.write(f"- {k}")
                        
        return adv.get("summary", "")


with tab_auto:
    st.subheader("Auto-Detect Check / स्वतः-पहचान जांच")
    uploaded_auto = st.file_uploader("Upload a crop or livestock photo / फ़सल या पशुधन की फ़ोटो अपलोड करें", type=["jpg", "jpeg", "png"], key="auto_upload")
    
    st.markdown("---")
    st.write("🎙️ **Voice Input (Hindi) / वॉयस इनपुट (हिंदी)** - *Optional / वैकल्पिक*")
    uploaded_voice = st.file_uploader("Upload audio (.wav) / ऑडियो अपलोड करें", type=["wav"], key="auto_voice_upload")
    if uploaded_voice and st.button("Transcribe Voice / आवाज़ को टेक्स्ट में बदलें", key="auto_voice_btn"):
        tmp_path = os.path.join(tempfile.gettempdir(), f"voice_{uploaded_voice.name}")
        with open(tmp_path, "wb") as f:
            f.write(uploaded_voice.getbuffer())
        with st.spinner("Transcribing..."):
            asr_res = hindi_asr.transcribe(tmp_path)
            transcript = asr_res.get("text", "")
        if transcript:
            st.success("Transcription complete!")
            st.write(f"**Transcript:** {transcript}")
            st.session_state.farmer_text_from_voice = transcript
            st.info("Transcript saved! You can now edit it below or click Auto-Detect.")

    farmer_text_auto = st.text_input("Farmer description / किसान का विवरण (लक्षण)", value=st.session_state.farmer_text_from_voice, key="auto_text")
    
    with st.expander("Livestock Sensors (Optional) / पशुधन सेंसर (वैकल्पिक)"):
        col1, col2, col3 = st.columns(3)
        with col1: temp_auto = st.slider("Temperature (°C) / तापमान", 35.0, 42.0, 38.5, key="auto_temp")
        with col2: activity_auto = st.selectbox("Activity Level / गतिविधि स्तर", ["normal / सामान्य", "low / कम", "high / अधिक"], key="auto_act")
        with col3: feed_auto = st.selectbox("Feed Intake / चारा खाना", ["normal / सामान्य", "low / कम", "none / कुछ नहीं"], key="auto_feed")
        sensor_data_auto = {"temperature": temp_auto, "activity": activity_auto, "feed_intake": feed_auto}
        
    if uploaded_auto and st.button("Auto-Detect / स्वतः विश्लेषण करें", key="auto_btn"):
        tmp_path = os.path.join(tempfile.gettempdir(), f"auto_{uploaded_auto.name}")
        with open(tmp_path, "wb") as f:
            f.write(uploaded_auto.getbuffer())
            
        with st.spinner("Auto-routing and analyzing..."):
            result = run_zone1_pipeline("auto", tmp_path, farmer_text=farmer_text_auto or None, sensor_reading=sensor_data_auto, mode=EXPERT_MODE)
            
        process_pipeline_result(result, farmer_text_auto)




with tab_history:
    st.subheader("Farm History Records / खेत के ऐतिहासिक रिकॉर्ड")
    st.write("Records saved locally in database. / रिकॉर्ड स्थानीय डेटाबेस में सहेजे गए हैं।")
    
    records = farm_memory.get_all_history_records(FARM_ID)
    if not records:
        st.info("No records found for this farm yet. / अभी तक कोई रिकॉर्ड नहीं मिला।")
    else:
        crop_records = [r for r in records if r.get("domain") == "crop"]
        ls_records = [r for r in records if r.get("domain") == "livestock"]
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 🌱 Crop History / फ़सल का इतिहास")
            if crop_records:
                st.dataframe(crop_records, use_container_width=True)
            else:
                st.write("No crop records.")
        with col2:
            st.markdown("### 🐄 Livestock History / पशुधन का इतिहास")
            if ls_records:
                st.dataframe(ls_records, use_container_width=True)
            else:
                st.write("No livestock records.")
