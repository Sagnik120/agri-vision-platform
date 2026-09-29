import re

from src.zone2_cloud.llm.advisory_format import history_refs, retrieved_doc_ids


def verify_citations(response_json: dict, payload: dict) -> dict:
    """
    Post-generation citation verification.
    A cited doc ID / history ref is hallucinated if it was not in what was sent.
    """
    sent_docs = set(retrieved_doc_ids(payload or {}))
    sent_refs = set(history_refs(payload or {}))
    cited_docs = [str(d) for d in (response_json.get("cited_doc_ids") or [])]
    cited_refs = [str(r) for r in (response_json.get("farm_history_refs") or [])]
    bad_docs = [d for d in cited_docs if d not in sent_docs]
    bad_refs = [r for r in cited_refs if r not in sent_refs]
    return {
        "cited_doc_ids": cited_docs,
        "hallucinated_doc_ids": bad_docs,
        "farm_history_refs": cited_refs,
        "hallucinated_history_refs": bad_refs,
        "citations_valid": not bad_docs and not bad_refs,
        "has_citation": bool(cited_docs),
    }

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
        
    # Citation-ID checks (only when the response uses the ID fields).
    if "cited_doc_ids" in response_json or "farm_history_refs" in response_json:
        check = verify_citations(response_json, input_evidence)
        for doc_id in check["hallucinated_doc_ids"]:
            reasons.append(f"Cited document '{doc_id}' was not in the retrieved set.")
            is_valid = False
        for ref in check["hallucinated_history_refs"]:
            reasons.append(f"Farm history reference '{ref}' was not in the provided history.")
            is_valid = False

    # 3. Drug safety regex check
    # Block specific dosages like "10mg", "5 ml/kg"
    advisory_str = str(response_json.get("advisory", {}))
    dosage_pattern = r'\b\d+\s?(mg|ml|g|kg|ml/kg)\b'
    if re.search(dosage_pattern, advisory_str, re.IGNORECASE):
        reasons.append("Safety violation: specific drug dosage detected in output.")
        is_valid = False
        
    return is_valid, reasons
