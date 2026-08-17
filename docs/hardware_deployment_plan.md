# Phase 4: Edge Deployment & Model Upgrade Plan

As the Agri-Vision Platform transitions from a hackathon prototype to a real-world deployment, the `mock_router` and `mock_classifier` modules must be swapped with quantized Edge AI models running on specialized hardware.

## 1. Hardware Architecture

To achieve the "Offline-First" constraint (Zone 1), the system must run on low-power, ruggedized edge hardware.

### Recommended Edge Node
- **Compute Board**: Raspberry Pi 5 (8GB) or NVIDIA Jetson Orin Nano (for higher throughput).
- **AI Accelerator**: Google Coral Edge TPU USB Accelerator. This will allow real-time inference of YOLO and MobileNet models at 30+ FPS while drawing less than 2W of power.
- **Sensors**: 
  - I2C Temperature/Humidity Sensor (e.g., DHT22).
  - LoRa/BLE beacons for tracking livestock activity levels (Accelerometer-based collars).
- **Power**: 12V Solar Panel + 20,000mAh Battery bank for remote farm operation.
- **Connectivity**: 4G/LTE Hat for the "Cloud Assist" escalation route (Zone 2) when offline inference fails.

## 2. Model Replacement Strategy

The current software architecture isolates the model inference behind `task_router.py` and `local_expert.py`. Replacing the mocks requires zero changes to the Streamlit UI or the Zone 2/Zone 3 modules.

### A. The Router (YOLOv8 Nano)
- **Current state**: `mock_router` uses basic keyword matching and random choice.
- **Production**: Train a YOLOv8-Nano object detection model on a dataset containing bounding boxes for `[Crop_Leaf, Cattle, Goat, Poultry]`.
- **Integration**: Export to `.tflite` (Edge TPU compiled) and load via PyCoral. If a `Crop_Leaf` is detected, route to the Crop Expert.

### B. The Crop Expert (MobileNetV3 or EfficientNet-Lite)
- **Current state**: `mock_classifier` returns pre-defined strings based on filename.
- **Production**: Train an EfficientNet-Lite0 model on the PlantVillage dataset (augmented with local Indian crop diseases). Quantize to INT8.
- **Integration**: 
  - The model outputs a softmax array. 
  - If the max confidence `> 0.85`, take the local route. 
  - If `< 0.85`, trigger the `route: cloud` protocol.

## 3. Containerization (Docker)

To deploy securely and cleanly across hundreds of edge nodes:
1. **Docker Compose**: Define two containers:
   - `agrivision-core`: Runs the Streamlit app, the local SQLite `farm_memory.db`, and the Edge TPU bindings.
   - `agrivision-sync`: A lightweight cron container that pushes SQLite history and RAG `.md` updates to a central cloud server whenever 4G connection is detected.

## 4. Immediate Next Steps for the Hackathon
If you have time during the hackathon, you can download a pre-trained **MobileNetV2 ImageNet model**, load it in `src/zone1_edge/vision/local_expert.py`, and run basic inference to prove that the pipeline can accept a real tensor output!
