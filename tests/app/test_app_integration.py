"""
test_app_integration.py — Integration tests for Streamlit app logic.
"""
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

# Mock Streamlit completely before importing the app
mock_st = MagicMock()
mock_st.tabs = MagicMock(side_effect=lambda x: [MagicMock()] * len(x))
mock_st.session_state = MagicMock()
mock_st.session_state.farmer_id = "FARM-001"
mock_st.session_state.__contains__.side_effect = lambda key: key in ["farmer_id", "farmer_text_from_voice"]
mock_st.columns.side_effect = lambda n: [MagicMock()] * n
mock_st.button.return_value = False
with patch.dict('sys.modules', {'streamlit': mock_st}):
    from src.app.streamlit_app import process_pipeline_result
    from src.zone3_memory.db import farm_memory


@pytest.fixture(autouse=True)
def setup_db(tmp_path):
    # Use a temporary DB for tests
    db_path = tmp_path / "test_memory.db"
    farm_memory.DEFAULT_DB_PATH = db_path
    farm_memory.init_db(str(db_path))
    yield
    # Cleanup happens automatically with tmp_path


@patch('src.app.streamlit_app.gemini_client.call_gemini')
@patch('src.app.streamlit_app.retriever.retrieve')
@patch('src.app.streamlit_app.st')
def test_process_pipeline_result_local(mock_st, mock_retrieve, mock_call_gemini):
    # 1. Setup a local-routed pipeline result (High Confidence)
    result = {
        "image_output": {"domain": "crop"},
        "sensor_output": None,
        "gate": {
            "route": "local",
            "prediction": "tomato_early_blight",
            "visual_confidence": 0.95,
            "final_confidence": 0.92
        },
        "local_advisory": {
            "summary": "Use copper fungicide.",
            "actions": ["Spray leaves"],
            "warning": None
        }
    }
    
    # 2. Execute
    summary = process_pipeline_result(result, "Farmer said brown spots")
    
    # 3. Verify
    assert summary == "Use copper fungicide."
    mock_call_gemini.assert_not_called()  # Should NOT hit cloud
    mock_retrieve.assert_not_called()
    
    # Verify DB persistence
    history = farm_memory.get_farm_history("FARM-001")
    assert "tomato_early_blight" in history
    assert "copper fungicide" in history


@patch('src.app.streamlit_app.gemini_client.call_gemini')
@patch('src.app.streamlit_app.retriever.retrieve')
@patch('src.app.streamlit_app.st')
def test_process_pipeline_result_cloud(mock_st, mock_retrieve, mock_call_gemini):
    # 1. Setup a cloud-routed pipeline result (Low Confidence / Anomaly)
    result = {
        "image_output": {"domain": "livestock"},
        "sensor_output": {"temperature": 41.5, "anomaly": True},
        "text_evidence": {"symptoms": ["fever"]},
        "gate": {
            "route": "cloud",
            "prediction": "lumpy_skin_disease",
            "visual_confidence": 0.55,
            "final_confidence": 0.50,
            "evidence_agreement": "low"
        },
        "local_advisory": None
    }
    
    mock_retrieve.return_value = "RAG context about lumpy skin."
    mock_call_gemini.return_value = {
        "diagnosis": {"condition": "Suspected Lumpy Skin Disease", "certainty": "probable"},
        "advisory": {"summary": "Isolate the cow.", "actions": [], "warning": "High fever"}
    }
    
    # 2. Execute
    summary = process_pipeline_result(result, "Cow is sick")
    
    # 3. Verify
    assert summary == "Isolate the cow."
    mock_retrieve.assert_called_once()
    mock_call_gemini.assert_called_once()
    
    # Verify DB persistence
    history = farm_memory.get_farm_history("FARM-001")
    assert "Suspected Lumpy Skin Disease" in history
    assert "Isolate the cow." in history
