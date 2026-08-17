import json
from pathlib import Path
from src.zone2_cloud.rag.retriever import retrieve

def test_rag_kb_schema_and_retrieval():
    kb_path = Path("src/zone1_edge/knowledge/local_advisories.json")
    with open(kb_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    for key, entry in data.items():
        assert "canonical_description" in entry or "summary" in entry
        assert "is_safety_critical" in entry
        assert isinstance(entry["is_safety_critical"], bool)
        assert "actions" in entry

    # Test retrieval
    results = retrieve("tomato with brown concentric spots on leaves", k=3)
    assert len(results) > 0
    assert "Tomato Early Blight" in results or "Tomato Late Blight" in results
