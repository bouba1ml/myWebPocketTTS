# WebPocketTTS 🎙️

A premium, local web interface for [Pocket TTS](https://github.com/kyutai-labs/pocket-tts). Generate high-quality speech and clone voices entirely on your CPU, wrapped in a modern dark-mode UI.

![WebPocketTTS UI](https://github.com/bouba1ml/myWebPocketTTS/raw/main/screenshot_placeholder.png) 
*(Note: You can replace this with a real screenshot)*

## ✨ Features

-   **Zero GPU Required**: Runs efficiently on CPU.
-   **Premium UI**: Glassmorphism design, mobile-responsive, and beautiful dark mode.
-   **Voice Cloning**: Upload a user reference audio file (`.wav`) to clone any voice instantly.
-   **Preset Voices**: access to high-quality built-in voices (Alba, Marius, etc.).
-   **FastAPI Backend**: Robust Python backend serving a static frontend.
-   **Safe Port**: Defaults to port `8543` to avoid conflicts with ComfyUI or other local tools.

## 🚀 Quick Start

### 1. Installation
Double-click `requirements.bat` to install dependencies.
*Alternatively, run:*
```bash
pip install -r requirements.txt
```

### 2. Authentication (Required for Voice Cloning)
To use the Voice Cloning feature, you need to authenticate with Hugging Face because the model is gated.

1.  Go to [Pocket TTS on Hugging Face](https://huggingface.co/kyutai/pocket-tts) and accept the license terms.
2.  Create a **Read** token in your [Hugging Face Settings](https://huggingface.co/settings/tokens).
3.  Double-click `setup_hf.bat` and paste your token when prompted.

### 3. Run
Double-click `run.bat`.
The app will open automatically at [http://localhost:8543](http://localhost:8543).

## 🛠️ Configuration

-   **Port**: The app runs on port `8543` by default. You can change this in `app.py` and `run.bat`.
-   **Environment**: Your Hugging Face token is stored in `.env` for the app to use.

## 📁 Project Structure

-   `app.py`: FastAPI backend and Pocket TTS integration.
-   `static/`: Frontend assets (HTML, CSS, JS).
-   `setup_hf.bat`: Authentication helper script.
-   `requirements.bat` / `run.bat`: One-click setup/start scripts.

## 🐛 Troubleshooting

**"Failed to load voice" (400 Error)**
-   Make sure you ran `setup_hf.bat`.
-   Verify you accepted the terms on the Hugging Face model page.
-   Restart `run.bat` after setting up auth.

**"Address already in use"**
-   `run.bat` automatically tries to kill old processes on port 8543.
-   If it persists, check if another app is using that port.

## 📜 Credits
Powered by [Pocket TTS](https://github.com/kyutai-labs/pocket-tts) from Kyutai Labs.
