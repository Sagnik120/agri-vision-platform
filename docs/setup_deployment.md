# Local Setup and Cloudflare Deployment Guide

This guide provides step-by-step instructions to set up Ollama for local Qwen inference and expose your platform to the internet using an accountless Cloudflare tunnel. The logs for the deployment will be saved to the `results` folder.

## Prerequisites
- You already have the Crop and Livestock models available locally.
- Ensure you have the `results` directory created in your project root to store logs. (e.g., `mkdir results\deployment` in PowerShell).

---

## Step 1: Install and Run Ollama (Local LLM Inference)

Ollama allows you to run large language models locally on your machine with minimal setup.

1. **Download Ollama:**
   - Go to [ollama.com/download](https://ollama.com/download) and download the Windows installer.
   - Install the application and make sure the Ollama background service is running (you should see the Ollama icon in your system tray).

2. **Download and Run Qwen:**
   - Open a new PowerShell window and run the following command to download and start the Qwen 1.5B model:
     ```powershell
     ollama run qwen2.5:1.5b
     ```
   - *Note: This will download the model. Once you see the `>>>` prompt, you can type `/bye` to exit. The Ollama server will keep running in the background on `http://localhost:11434`.*

3. **Configure the App Environment:**
   - Open your `.env` file and ensure it points to your local Ollama server. Update or add these variables:
     ```env
     ADVISORY_BACKEND=local_llm
     LOCAL_LLM_URL=http://localhost:11434/v1
     LOCAL_LLM_MODEL=qwen2.5:1.5b
     ```

---

## Step 2: Start the Streamlit Application

1. Open a PowerShell window in your project root (`d:\Projects\SIH_Agri_Vision\Codebase\agri-vision-platform`).
2. Activate your virtual environment:
   ```powershell
   .\venv\Scripts\Activate
   ```
3. Run the Streamlit app and pipe the logs to the results folder:
   ```powershell
   mkdir -Force results\deployment
   streamlit run src/app/streamlit_app.py > results\deployment\streamlit.log 2>&1
   ```
   *(The app is now running locally, usually on `http://localhost:8501`. You won't see the output in the console because it is being saved to the log file).*

---

## Step 3: Expose to the Internet via Cloudflare (Accountless)

We will use Cloudflare Tunnel in Quick/Accountless mode to securely expose your local Streamlit app to the public internet.

1. **Download Cloudflared (Windows):**
   - Download the `cloudflared.exe` executable for Windows from the [official Cloudflare releases page](https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe).
   - Move the downloaded `cloudflared-windows-amd64.exe` to your project root folder and rename it to `cloudflared.exe`.

2. **Run the Tunnel:**
   - Open a **new** PowerShell window in your project root.
   - Run the following command to create the tunnel and save the logs (which contain your public URL) to the results folder:
     ```powershell
     .\cloudflared.exe tunnel --url http://localhost:8501 > results\deployment\cloudflare.log 2>&1
     ```

3. **Get Your Public URL:**
   - Since the tunnel process is running in the background and logging to a file, you need to read the log file to find your public `.trycloudflare.com` link.
   - Open another PowerShell window and run:
     ```powershell
     Select-String -Path "results\deployment\cloudflare.log" -Pattern "trycloudflare.com"
     ```
   - You will see an output containing a URL that looks like `https://<random-words>.trycloudflare.com`. 
   - **This is your public deployment link!** You can share this link with anyone, and it will serve your local Streamlit app.

---

## Shutdown Instructions
When you are done testing/demoing:
1. Go to the PowerShell window running `cloudflared.exe` and press `Ctrl+C` to stop the tunnel.
2. Go to the PowerShell window running `streamlit run` and press `Ctrl+C` to stop the web app.
3. You can quit Ollama from the Windows system tray.
