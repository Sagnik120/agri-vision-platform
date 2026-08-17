import json

data = json.load(open('src/zone1_edge/knowledge/local_advisories.json'))

for key, entry in data.items():
    entry['canonical_description'] = entry['summary']
    if key in ['tomato_late_blight', 'potato_late_blight', 'lumpy_skin_disease', 'foot_and_mouth_disease']:
        entry['is_safety_critical'] = True
    else:
        entry['is_safety_critical'] = False

# Add a few more entries to hit ~20 entries for B1
extra_entries = {
    "wheat_rust": {
        "summary": "Fungal disease causing orange/brown pustules on wheat leaves.",
        "actions": [
            "Apply systemic fungicides (e.g. tebuconazole) at first sign.",
            "Use resistant wheat varieties in future."
        ],
        "warning": "Can cause severe yield loss if not treated before heading.",
        "canonical_description": "Fungal disease causing orange/brown pustules on wheat leaves.",
        "is_safety_critical": False
    },
    "rice_blast": {
        "summary": "Devastating fungal disease causing diamond-shaped lesions on rice leaves.",
        "actions": [
            "Maintain proper flooding in paddies.",
            "Avoid excessive nitrogen fertilization.",
            "Apply tricyclazole or similar fungicide."
        ],
        "warning": "Highly destructive; treat early.",
        "canonical_description": "Devastating fungal disease causing diamond-shaped lesions on rice leaves.",
        "is_safety_critical": True
    },
    "cotton_bollworm": {
        "summary": "Pest larvae that feed on cotton bolls, destroying the fiber.",
        "actions": [
            "Monitor with pheromone traps.",
            "Apply targeted insecticides if threshold is reached.",
            "Destroy crop residues after harvest."
        ],
        "warning": "Pests can develop resistance; rotate chemicals.",
        "canonical_description": "Pest larvae that feed on cotton bolls, destroying the fiber.",
        "is_safety_critical": False
    },
    "poultry_avian_influenza": {
        "summary": "Highly contagious viral disease in poultry causing sudden death and respiratory distress.",
        "actions": [
            "Isolate the flock immediately.",
            "Report to veterinary authorities.",
            "Implement strict biosecurity and cull infected birds."
        ],
        "warning": "Zoonotic potential! Notify authorities immediately.",
        "canonical_description": "Highly contagious viral disease in poultry causing sudden death and respiratory distress.",
        "is_safety_critical": True
    },
    "poultry_newcastle_disease": {
        "summary": "Viral disease in birds causing twisting of the neck, paralysis, and drop in egg production.",
        "actions": [
            "Vaccinate healthy birds immediately.",
            "Isolate sick birds.",
            "Disinfect premises thoroughly."
        ],
        "warning": "Highly contagious; strict quarantine required.",
        "canonical_description": "Viral disease in birds causing twisting of the neck, paralysis, and drop in egg production.",
        "is_safety_critical": True
    },
    "goat_peste_des_petits_ruminants": {
        "summary": "Severe viral disease (PPR) of sheep and goats causing fever, sores in the mouth, and diarrhea.",
        "actions": [
            "Quarantine new animals.",
            "Vaccinate flock.",
            "Provide supportive care and antibiotics for secondary infections."
        ],
        "warning": "High mortality rate; notify vet services.",
        "canonical_description": "Severe viral disease (PPR) of sheep and goats causing fever, sores in the mouth, and diarrhea.",
        "is_safety_critical": True
    },
    "soybean_rust": {
        "summary": "Aggressive fungal disease causing premature defoliation in soybean.",
        "actions": [
            "Apply fungicide immediately upon detection.",
            "Ensure good canopy penetration of spray."
        ],
        "warning": "Can spread rapidly by wind.",
        "canonical_description": "Aggressive fungal disease causing premature defoliation in soybean.",
        "is_safety_critical": False
    },
    "citrus_canker": {
        "summary": "Bacterial disease causing raised corky lesions on citrus leaves, stems, and fruit.",
        "actions": [
            "Use copper-based sprays preventatively.",
            "Prune and destroy infected branches.",
            "Decontaminate tools between trees."
        ],
        "warning": "Highly contagious in wet conditions.",
        "canonical_description": "Bacterial disease causing raised corky lesions on citrus leaves, stems, and fruit.",
        "is_safety_critical": False
    },
    "mango_anthracnose": {
        "summary": "Fungal disease causing dark irregular spots on leaves, blossoms, and fruits of mango.",
        "actions": [
            "Apply fungicides during flowering and early fruit set.",
            "Prune canopy for better aeration."
        ],
        "warning": "Can cause severe post-harvest rot.",
        "canonical_description": "Fungal disease causing dark irregular spots on leaves, blossoms, and fruits of mango.",
        "is_safety_critical": False
    }
}
data.update(extra_entries)

with open('src/zone1_edge/knowledge/local_advisories.json', 'w') as f:
    json.dump(data, f, indent=2)

print("Updated local_advisories.json")
