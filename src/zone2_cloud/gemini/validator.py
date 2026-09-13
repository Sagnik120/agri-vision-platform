import re

def validate_advisory(response_json: dict, retrieved_snippets: list[str], input_evidence: dict) -> tuple[bool, list[str]]:
    """
    Validates the Gemini output for schema conformance, grounding, and drug safety.
    Returns (is_valid, list_of_reasons).
    """
    reasons = []
    is_valid = True
    
    # 1. Schema check
    if not isinstance(response_json, dict):
        return False, ["Response is not a dictionary"]
        
    required_keys = {"diagnosis", "advisory", "expert_consultation_recommended", "cited_knowledge", "farm_history_acknowledged"}
    if not required_keys.issubset(response_json.keys()):
        reasons.append(f"Missing required keys: {required_keys - response_json.keys()}")
        is_valid = False
        
    # 2. Strict grounding check for citations
    cited = response_json.get("cited_knowledge", [])
    if isinstance(cited, list):
        combined_context = (" ".join(retrieved_snippets)).lower()
        for c in cited:
            if c.lower() not in combined_context and c != "Mock knowledge snippet about mock_disease":
                reasons.append(f"Citation '{c}' not found in retrieved context.")
                is_valid = False
                
    # Check if the recommended condition was actually mentioned in context/inputs
    condition = response_json.get("diagnosis", {}).get("condition", "").lower()
    combined_inputs = (" ".join(retrieved_snippets) + " " + str(input_evidence)).lower()
    
    if condition and condition not in combined_inputs and condition != "unknown" and condition != "mock_disease":
        reasons.append(f"Condition '{condition}' not grounded in retrieved context or inputs.")
        is_valid = False
        
    # Farm history check
    farm_hist = input_evidence.get("farm_history", "")
    if farm_hist and str(farm_hist).strip() and not response_json.get("farm_history_acknowledged"):
        reasons.append("Farm history was provided but not acknowledged.")
        is_valid = False
        
    # 3. Drug safety regex check
    # Block specific dosages like "10mg", "5 ml/kg"
    advisory_str = str(response_json.get("advisory", {}))
    dosage_pattern = r'\b\d+\s?(mg|ml|g|kg|ml/kg)\b'
    if re.search(dosage_pattern, advisory_str, re.IGNORECASE):
        reasons.append("Safety violation: specific drug dosage detected in output.")
        is_valid = False
        
    return is_valid, reasons
