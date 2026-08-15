"""
streamlit_app.py — STUB. Person B, Zone shell (Hour 6:45-7:30 of the plan).

GOAL: 3 tabs (Crop, Livestock, Voice); top banner 🟢 LOCAL MODE / 🟡 CLOUD
ASSIST; "Why cloud?" panel showing confidence % + evidence conflict.
Wires Person A's Zone 1 pipeline + Person B's Zone 2/3 modules together.

This file currently only proves Person A's pipeline is callable from
Streamlit — Person B extends it with ASR/TTS/Gemini/farm-memory wiring per
the TODOs marked below.

Run with:
    streamlit run src/app/streamlit_app.py

TODO (Person B):
  1. Voice tab: record/upload audio -> src.zone2_cloud.asr.hindi_asr.transcribe()
     -> feed transcript text into the Crop/Livestock tab's `farmer_text` field.
  2. On "Analyze" click: call run_zone1_pipeline(...), branch on
     result["gate"]["route"]:
       - "local"  -> show result["local_advisory"] directly, 🟢 banner.
       - "cloud"  -> build contract #6 payload (see
         zone1_edge.pipeline.build_cloud_payload_stub for the shape), fill in
         real farmer_text + retrieved_knowledge (rag.retriever.retrieve) +
         farm_history (zone3_memory.db.farm_memory.get_farm_history), call
         gemini_client.call_gemini(payload), show the result, 🟡 banner.
  3. "Why cloud?" expander: show gate["final_confidence"], gate["evidence_agreement"],
     and gate["_debug_gate"] contents in plain language.
  4. After every run (local or cloud): call farm_memory.save_observation /
     save_diagnosis / save_advisory so the "My Farm — History Timeline"
     (Zone 3) can show it, and so a repeat case triggers the "recorded N
     days ago" line in the final demo.
  5. Call hindi_tts.synthesize() on the final advisory text and play it back
     with st.audio().
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import streamlit as st

from src.zone1_edge.pipeline import run_zone1_pipeline, build_cloud_payload_stub

st.set_page_config(page_title="Agri-Vision Platform", layout="wide")
st.title("🌾 Unified AI Agri-Vision Platform")
st.caption("Crop Disease ID + Livestock Monitoring + Historical Records — Offline-First")

tab_crop, tab_livestock, tab_voice = st.tabs(["🌱 Crop", "🐄 Livestock", "🎙️ Voice"])

with tab_crop:
    st.subheader("Crop Disease Check")
    uploaded = st.file_uploader("Upload a crop photo", type=["jpg", "jpeg", "png"], key="crop_upload")
    farmer_text_crop = st.text_input("Farmer description (optional — normally comes from Voice tab)", key="crop_text")
    if uploaded and st.button("Analyze Crop", key="crop_btn"):
        tmp_path = f"/tmp/{uploaded.name}"
        with open(tmp_path, "wb") as f:
            f.write(uploaded.getbuffer())
        result = run_zone1_pipeline("crop", tmp_path, farmer_text=farmer_text_crop or None, mode="auto")
        gate = result["gate"]
        if gate["route"] == "local":
            st.success(f"🟢 LOCAL DECISION — {gate['prediction']} (confidence {gate['final_confidence']:.0%})")
            adv = result["local_advisory"]
            st.write(adv["summary"])
            for a in adv["actions"]:
                st.write(f"- {a}")
            if adv["warning"] != "None — recheck if new symptoms appear.":
                st.warning(adv["warning"])
        else:
            st.warning(f"🟡 CLOUD ASSIST needed — confidence {gate['final_confidence']:.0%}, "
                       f"evidence agreement: {gate['evidence_agreement']}")
            st.info("TODO(Person B): call Gemini here via build_cloud_payload_stub() "
                    "+ rag.retriever.retrieve() + zone3_memory.get_farm_history(), "
                    "then gemini_client.call_gemini(payload).")
        with st.expander("Why this decision? (debug)"):
            st.json(gate)

with tab_livestock:
    st.subheader("Livestock Health Check")
    st.info("TODO(Person B): same pattern as Crop tab, plus sensor_reading inputs "
            "(temperature/activity/feed_intake sliders) passed to run_zone1_pipeline().")

with tab_voice:
    st.subheader("Voice Input (Hindi)")
    st.info("TODO(Person B): audio upload/record -> src.zone2_cloud.asr.hindi_asr.transcribe() "
            "-> feed transcript into Crop/Livestock tabs' farmer_text field via st.session_state.")

st.divider()
st.caption("Zone 1 (Person A) is fully wired above. Zone 2/3 cloud+voice+memory features "
           "are stubbed — see src/zone2_cloud/PERSON_B_README.md for the build plan.")
