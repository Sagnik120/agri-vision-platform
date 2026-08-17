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
        
    required_keys = {"diagnosis", "advisory", "expert_consultation_recommended", "cited_knowledge"}
    if not required_keys.issubset(response_json.keys()):
        reasons.append(f"Missing required keys: {required_keys - response_json.keys()}")
        is_valid = False
        
    # 2. Crude grounding check
    # Check if the recommended condition was actually mentioned in context/snippets
    condition = response_json.get("diagnosis", {}).get("condition", "").lower()
    combined_context = (" ".join(retrieved_snippets) + " " + str(input_evidence)).lower()
    
    if condition and condition not in combined_context and condition != "unknown" and condition != "mock_disease":
        reasons.append(f"Condition '{condition}' not grounded in retrieved context or inputs.")
        is_valid = False
        
    # 3. Drug safety regex check
    # Block specific dosages like "10mg", "5 ml/kg"
    advisory_str = str(response_json.get("advisory", {}))
    dosage_pattern = r'\b\d+\s?(mg|ml|g|kg|ml/kg)\b'
    if re.search(dosage_pattern, advisory_str, re.IGNORECASE):
        reasons.append("Safety violation: specific drug dosage detected in output.")
        is_valid = False
        
    return is_valid, reasons
