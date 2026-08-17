import json
import os
from pathlib import Path

# Load advisories
kb_json_path = Path("src/zone1_edge/knowledge/local_advisories.json")
with open(kb_json_path, "r", encoding="utf-8") as f:
    data = json.load(f)

# Clear old MD files
kb_dir = Path("src/zone2_cloud/rag/knowledge_base")
kb_dir.mkdir(parents=True, exist_ok=True)
for md_file in kb_dir.glob("*.md"):
    if md_file.name != "README.md":
        md_file.unlink()

# Write new MD files
for key, entry in data.items():
    md_content = f"# {key.replace('_', ' ').title()}\n\n"
    md_content += f"**Description:** {entry.get('canonical_description', entry.get('summary', ''))}\n\n"
    md_content += f"**Safety Critical:** {entry.get('is_safety_critical', False)}\n\n"
    md_content += "## Actions\n"
    for action in entry.get("actions", []):
        md_content += f"- {action}\n"
    md_content += f"\n## Warning\n{entry.get('warning', 'None')}\n"
    
    with open(kb_dir / f"{key}.md", "w", encoding="utf-8") as f:
        f.write(md_content)

print(f"Generated {len(data)} markdown files for RAG KB.")
