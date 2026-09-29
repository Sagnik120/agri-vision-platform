"""
kb_coverage_audit.py — Does every class an expert can predict have a KB document
(cloud RAG) and a local offline advisory? Offline, no model loading.

Class sources: MoE groups (PlantVillage + livestock), the current crop checkpoint's
config.json labels (if downloaded) and the mock label sets.

    python eval/kb_coverage_audit.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.zone1_edge import config  # noqa: E402
from src.zone1_edge.experts.crop_expert import CROP_MOCK_LABELS  # noqa: E402
from src.zone1_edge.experts.livestock_expert import LIVESTOCK_MOCK_LABELS  # noqa: E402
from src.zone1_edge.knowledge.label_aliases import normalize_condition  # noqa: E402
from src.zone1_edge.moe.expert_groups import DOMAIN_GROUPS  # noqa: E402


def predictable_labels() -> dict[str, str]:
    labels = {}
    for domain, groups in DOMAIN_GROUPS.items():
        for g, classes in groups.items():
            for c in classes:
                labels[c] = f"moe:{g}"
    cfg = config.CROP_MODEL_LOCAL_DIR / "config.json"
    if cfg.exists():
        for l in json.loads(cfg.read_text(encoding="utf-8")).get("id2label", {}).values():
            labels.setdefault(l, "current_crop_checkpoint")
    for l in CROP_MOCK_LABELS + LIVESTOCK_MOCK_LABELS:
        labels.setdefault(l, "mock_labels")
    return labels


def main():
    kb_docs = {p.stem for p in (ROOT / "src/zone2_cloud/rag/knowledge_base").glob("*.md")}
    local = set(json.loads((config.KNOWLEDGE_DIR / "local_advisories.json").read_text(encoding="utf-8")))
    rows, gaps_kb, gaps_local = [], [], []
    for label, src in sorted(predictable_labels().items()):
        key = normalize_condition(label)
        if key == "invalid":  # checkpoint's reject class, not a condition
            continue
        in_kb, in_local = key in kb_docs, key in local
        rows.append((label, key, src, in_kb, in_local))
        if not in_kb:
            gaps_kb.append(key)
        if not in_local:
            gaps_local.append(key)
    print(f"{'label':55} {'kb_key':40} kb  local")
    for label, key, src, a, b in rows:
        print(f"{label[:55]:55} {key[:40]:40} {'Y' if a else '-'}   {'Y' if b else '-'}")
    print(f"\nRAG KB gaps ({len(set(gaps_kb))}): {sorted(set(gaps_kb))}")
    print(f"Local offline advisory gaps ({len(set(gaps_local))}) -> these always escalate to cloud: {sorted(set(gaps_local))}")


if __name__ == "__main__":
    main()
