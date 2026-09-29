"""
kb_metadata.py — Knowledge-base document metadata (Zone 2).

Each KB markdown file may start with a simple frontmatter block:
    ---
    doc_id: KB-tomato_late_blight
    condition: tomato_late_blight
    domain: crop
    source: Agri-Vision Local KB v2.0
    region: India (general)
    last_updated: 2026-09-29
    review_status: draft_needs_expert_review
    ---
No YAML dependency: flat `key: value` lines only. Missing fields are derived
from the filename, so `doc_id` is always stable (`KB-<file stem>`), even for
files regenerated without frontmatter (e.g. by sync_kb.py).
"""

from __future__ import annotations

from pathlib import Path

LIVESTOCK_CONDITIONS = {
    "lumpy_skin_disease", "foot_and_mouth_disease", "healthy", "mastitis_suspected",
    "abnormal_temperature", "livestock_heat_stress", "livestock_ketosis",
    "goat_peste_des_petits_ruminants", "poultry_avian_influenza", "poultry_newcastle_disease",
}


def parse_frontmatter(text: str) -> tuple[dict, str]:
    if not text.startswith("---"):
        return {}, text
    parts = text.split("\n")
    meta = {}
    for i, line in enumerate(parts[1:], start=1):
        if line.strip() == "---":
            return meta, "\n".join(parts[i + 1:]).strip()
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip()
    return {}, text  # unterminated block: treat whole file as body


def doc_id_for(stem: str) -> str:
    return f"KB-{stem}"


def load_doc(path: Path) -> dict:
    meta, body = parse_frontmatter(path.read_text(encoding="utf-8").strip())
    condition = meta.get("condition", path.stem)
    return {
        "doc_id": meta.get("doc_id", doc_id_for(path.stem)),
        "condition": condition,
        "domain": meta.get("domain", "livestock" if condition in LIVESTOCK_CONDITIONS else "crop"),
        "source": meta.get("source", "Agri-Vision Local KB"),
        "region": meta.get("region", "India (general)"),
        "last_updated": meta.get("last_updated", ""),
        "review_status": meta.get("review_status", "unreviewed"),
        "text": body,
    }


def load_kb(kb_dir: Path) -> list[dict]:
    return [load_doc(p) for p in sorted(kb_dir.glob("*.md")) if p.name != "README.md"]
