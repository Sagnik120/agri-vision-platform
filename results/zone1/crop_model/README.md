# results/zone1/crop_model/

This folder stores OUTPUT ARTIFACTS from the crop expert model — not the
model weights themselves (those live in `models_cache/crop_model/`, git-ignored).

Expected contents once you run the real model on your Mac:
- `sample_predictions.json` — batch of predictions on demo_data/crop/*.jpg
- `model_info.json` — which HF repo id actually loaded (from crop_expert.backend_info)
- `inference_benchmark.json` — load time + per-image inference time

Generate these by running:
    python -m src.zone1_edge.experts.crop_expert demo_data/crop/<image>.jpg
