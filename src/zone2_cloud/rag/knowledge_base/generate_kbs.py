import os
from pathlib import Path

kb_dir = Path(__file__).resolve().parent

kbs = {
    "tomato_early_blight.md": """# Condition: Tomato Early Blight

## Symptoms
- Brown spots on older leaves, often with concentric rings (bullseye appearance).
- Yellowing of leaves around the spots.
- Defoliation starting from the bottom of the plant.

## Visual Indicators
- Target-like spots on leaves.
- Dark, sunken lesions on stems.

## Recommended Actions
- Apply copper-based fungicides immediately.
- Remove and destroy severely infected lower leaves.
- Ensure good air circulation by staking or pruning.

## Prevention
- Practice crop rotation.
- Use drip irrigation instead of overhead watering.
- Plant resistant varieties.

## When to Seek Expert Help
- If the disease spreads rapidly despite fungicide application.
- If young plants or stems are heavily infected.

## Source
Agricultural Extension Service - Tomato Disease Guide
""",
    "tomato_late_blight.md": """# Condition: Tomato Late Blight

## Symptoms
- Large, irregular, water-soaked spots on leaves.
- White fungal growth on the underside of leaves during humid weather.
- Dark, greasy-looking spots on stems.
- Firm, dark brown lesions on fruit.

## Visual Indicators
- Rapidly expanding dark lesions on leaves and stems.
- White mold under leaves in high humidity.

## Recommended Actions
- Immediately remove and destroy infected plants; do not compost.
- Apply protective fungicides (like chlorothalonil or copper) if weather is cool and wet.

## Prevention
- Avoid overhead watering.
- Destroy volunteer tomato and potato plants.
- Ensure good spacing for airflow.

## When to Seek Expert Help
- As soon as late blight is suspected, as it is highly contagious and devastating.

## Source
National Plant Disease Information System
""",
    "potato_early_blight.md": """# Condition: Potato Early Blight

## Symptoms
- Dark, concentric ringed spots on older leaves.
- Leaves turn yellow and dry up.
- Sunken, dark, dry rot on potato tubers.

## Visual Indicators
- "Bullseye" pattern lesions on leaves.

## Recommended Actions
- Apply appropriate fungicides containing chlorothalonil or mancozeb.
- Keep plants well-fertilized to reduce susceptibility.

## Prevention
- Harvest only when vines are completely dead to protect tubers.
- Rotate crops with non-solanaceous plants.

## When to Seek Expert Help
- If defoliation is severe early in the season.

## Source
Potato Growers Association Guidelines
""",
    "potato_late_blight.md": """# Condition: Potato Late Blight

## Symptoms
- Irregular, pale green, water-soaked spots on leaves.
- Lesions turn dark brown/black rapidly.
- White fuzzy growth on leaf undersides in wet conditions.
- Tubers show reddish-brown, dry, granular rot under the skin.

## Visual Indicators
- Rapid blighting of foliage.
- White mold on the underside of leaf lesions.

## Recommended Actions
- Destroy infected foliage immediately.
- Apply systemic fungicides if the infection is caught very early.

## Prevention
- Plant certified disease-free seed potatoes.
- Eliminate cull piles and volunteer potatoes.

## When to Seek Expert Help
- Immediate reporting to local agricultural extension is often required as it can destroy entire fields in days.

## Source
International Potato Center
""",
    "maize_common_rust.md": """# Condition: Maize Common Rust

## Symptoms
- Small, reddish-brown pustules forming on both upper and lower leaf surfaces.
- Pustules rupture, releasing powdery, rust-colored spores.
- Leaves may yellow and dry prematurely if infection is severe.

## Visual Indicators
- Rust-colored, powdery bumps on leaves.

## Recommended Actions
- Apply foliar fungicides if the disease is detected early, especially before silking.
- Ensure balanced nutrition, particularly potassium.

## Prevention
- Plant rust-resistant maize hybrids.
- Avoid planting in extremely humid, cool environments if possible.

## When to Seek Expert Help
- If pustules cover more than 5% of the leaf area before the tasseling stage.

## Source
Maize Pathology Handbook
""",
    "maize_leaf_blight.md": """# Condition: Maize Northern Corn Leaf Blight

## Symptoms
- Long, elliptical, grayish-green or tan lesions on leaves.
- Lesions can be 1 to 6 inches long and resemble the shape of a cigar.
- Lower leaves are infected first, progressing upwards.

## Visual Indicators
- Cigar-shaped necrotic lesions.

## Recommended Actions
- Apply fungicides at the tasseling stage if lesions are present on or above the ear leaf.
- Deep plow residue to bury infected material.

## Prevention
- Select resistant hybrids.
- Implement crop rotation.

## When to Seek Expert Help
- If significant lesion development occurs before the grain-fill period.

## Source
Corn Disease Diagnostic Guide
""",
    "lumpy_skin_disease.md": """# Condition: Lumpy Skin Disease (Cattle)

## Symptoms
- High fever, increased nasal and eye discharge.
- Firm, circumscribed skin nodules (lumps) of 1-5 cm developing across the body.
- Swollen lymph nodes.
- Significant drop in milk production.

## Visual Indicators
- Distinctive skin nodules/lumps on the head, neck, limbs, and udder.

## Recommended Actions
- Isolate infected animals immediately.
- Treat secondary bacterial infections with antibiotics (consult a vet).
- Provide supportive care (soft feed, water).

## Prevention
- Vaccinate healthy animals.
- Control vectors (mosquitoes, biting flies, ticks) using insect repellents and environmental management.

## When to Seek Expert Help
- IMMEDIATELY. LSD is a notifiable disease in many regions and requires veterinary confirmation.

## Source
World Organisation for Animal Health (WOAH)
""",
    "foot_and_mouth_disease.md": """# Condition: Foot and Mouth Disease (FMD)

## Symptoms
- High fever for two to three days.
- Blisters (vesicles) inside the mouth, on the tongue, and on the hooves.
- Excessive salivation and drooling.
- Lameness and reluctance to move.

## Visual Indicators
- Ruptured blisters leaving raw erosions on gums, tongue, and teats.
- Drooling and lameness.

## Recommended Actions
- Strict quarantine of the affected farm. No movement of animals, equipment, or people.
- Contact veterinary authorities immediately.

## Prevention
- Strict biosecurity measures.
- Vaccination programs depending on the region's endemic status.

## When to Seek Expert Help
- IMMEDIATELY upon suspicion. FMD is highly contagious and economically devastating.

## Source
Veterinary Epidemiology Center
"""
}

for filename, content in kbs.items():
    with open(kb_dir / filename, "w") as f:
        f.write(content)

print(f"Generated {len(kbs)} KB entries.")
