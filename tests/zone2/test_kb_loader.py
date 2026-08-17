import pytest
from src.zone1_edge.knowledge.kb_loader import get_safety_critical_conditions

def test_get_safety_critical_conditions():
    critical = get_safety_critical_conditions()
    
    assert isinstance(critical, set)
    assert len(critical) > 0
    assert "lumpy_skin_disease" in critical
    assert "foot_and_mouth_disease" in critical
    
    # Check one that should NOT be critical
    assert "tomato_early_blight" not in critical
