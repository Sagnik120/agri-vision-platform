"""
Task A6 - Explainability (Lightweight)
"""

def format_top3(top_k: list) -> dict:
    """
    Format the top_k list for display.
    Expects top_k in format: [["prediction_name", confidence_float], ...]
    Returns a dict mapping rank (1, 2, 3) to the prediction.
    """
    result = {}
    for i, item in enumerate(top_k[:3]):
        result[f"rank_{i+1}"] = {"label": item[0], "confidence": item[1]}
    return result

def format_reason(threshold_reason: list, advisory_tier: str) -> str:
    """
    Joins the reason list into a readable sentence.
    """
    if not threshold_reason:
        return f"Routed to {advisory_tier} tier."
    
    reasons_str = ", ".join(threshold_reason)
    return f"Routed to {advisory_tier} tier because: {reasons_str}."

# TODO (stretch, see Section 9): grad-cam overlay
