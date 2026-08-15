# results/zone1/fusion_runs/

Stores JSON dumps of full pipeline runs (image + text + sensor -> fusion ->
gate -> advisory) for the 4 fixed demo sentences referenced in the plan's
Section 6 Final Test row. Useful for judges / debugging to see exactly why
a case routed local vs cloud.

Generate with:
    python -m src.zone1_edge.pipeline --domain crop --image demo_data/crop/sample1.jpg --text "..." > results/zone1/fusion_runs/case1.json
