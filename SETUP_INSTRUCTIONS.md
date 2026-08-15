# Setup and Verification Instructions

### 1. Setup Instructions
First, ensure you are in the project root (`d:\Projects\SIH_Agri_Vision\agri-vision-platform`).

**Step A: Update Pip and Create a Virtual Environment**
Run the following commands in PowerShell to create an isolated environment, ensuring a clean installation without affecting your global Python setup:

```powershell
# Upgrade your global pip first (optional but recommended)
python -m pip install --upgrade pip

# Create a virtual environment named 'venv'
python -m venv venv

# Activate the virtual environment
.\venv\Scripts\Activate.ps1

# Upgrade pip inside the virtual environment
python -m pip install --upgrade pip
```

**Step B: Install the Dependencies**
With the virtual environment activated (you should see `(venv)` in your prompt), run the following command to install everything at once:

```powershell
# Install all required dependencies directly from requirements.txt
pip install -r requirements.txt
```
*(Note: If you run into any issues installing FAISS on Windows, you can optionally swap to chromadb as permitted in requirements.txt, but faiss-cpu usually installs fine via pip.)*

**Important:** For the ASR (Speech-to-Text) module to function properly, **FFmpeg** is required by `librosa`. Please ensure FFmpeg is installed and added to your system's PATH. On Windows, you can do this easily via winget:
```powershell
winget install ffmpeg
```

**Step C: Configure the Environment**
1. Copy the `.env.example` file to `.env`:
```powershell
Copy-Item .env.example .env
```
2. Open `.env` and configure your API keys. 
   - To use the real Gemini cloud fallback (Zone 2), set `GEMINI_ENABLED=true` and `GEMINI_API_KEY=your_actual_key`.
   - If you don't have a key yet and want to use the deterministic mock response for UI testing, leave `GEMINI_ENABLED=false`.

**Step D: Setup Hugging Face Speech Models (Offline)**
Since Hugging Face models (for ASR and TTS) can be large, we have configured the app to read them directly from a local `models_cache` folder rather than attempting to download them on the fly.
If your teammate provided you with the zipped models:
1. Create a directory named `models_cache` in the project root if it doesn't exist.
2. Extract the ASR model zip inside `models_cache/asr/`. The path should look like this:
   `models_cache/asr/indicconformer-hi-hybrid-rnnt-large-hf/`
3. Extract the TTS model zip inside `models_cache/tts/`. The app will automatically detect any valid model folder here. The path should look like this:
   `models_cache/tts/<your_model_folder>/` (e.g., `models_cache/tts/vits_rasa_13/`)
   
*(If you are missing these models, the pipeline will still run safely by falling back to deterministic mock text/audio for the sake of the UI demo.)*

**Step E: Download Offline Vision Models**
To ensure the edge-first architecture runs smoothly offline, run the following setup scripts to download the specialized vision (Crop/Livestock) models locally:

```powershell
python setup/download_crop_model.py
python setup/download_livestock_model.py
```

---

### 2. What to Check in the Implementation

To verify that the entire architecture is working correctly, you should run the Streamlit app (make sure your `venv` is still activated):

```powershell
streamlit run src/app/streamlit_app.py
```

Then, perform the following verification steps:

**Test the Offline Voice Tab (ASR):**
1. Go to the Voice tab and upload a test `.wav` file.
2. Click "Transcribe Voice".
3. **Expected:** It should attempt to load the IndicConformer model. If the model isn't downloaded, it will safely fall back to the deterministic Mock ASR and save the transcript to your session.

**Test the Local Path (High Confidence):**
1. Go to the Crop tab.
2. Upload a test crop image and ensure the farmer text is present.
3. Click "Analyze Crop".
4. **Expected:** Assuming the simulated confidence gate returns a high score, you should see the 🟢 LOCAL DECISION banner. The UI should display the advisory instantly without any network calls, proving the edge-first architecture.

**Test the Cloud Path (Low Confidence):**
1. Go to the Livestock tab.
2. Upload an image, and set the simulated sensor sliders to anomalous values (e.g., extremely low feed intake and high temperature).
3. Click "Analyze Livestock".
4. **Expected:** The confidence gate should detect the anomaly and flag a 🟡 CLOUD ASSIST escalation. It will retrieve RAG snippets, fetch the Farm History from SQLite, and hit the Gemini Client. If `GEMINI_ENABLED=false`, you will see the deterministic mock cloud response.

**Verify Farm Memory Persistence (SQLite):**
1. After running the analyses above, re-run another analysis for either Crop or Livestock.
2. **Expected:** When escalating to the cloud, the RAG/History spinner will run, and the `build_cloud_payload_stub` will successfully package the previous diagnoses (e.g., "0 days ago: Mock Disease...").

**Test Offline TTS:**
1. On any completed advisory, click the "Play Advisory (Hindi TTS)" button.
2. **Expected:** It should gracefully fall back to the mock audio file generator if the FastPitch or other HF TTS models (e.g., `vits_rasa_13`) aren't cached locally.
