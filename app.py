import os
import io
import time
import logging
import scipy.io.wavfile
import numpy as np
from fastapi import FastAPI, HTTPException, BackgroundTasks, UploadFile, File, Form
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from pocket_tts import TTSModel
import shutil
import huggingface_hub

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="WebPocketTTS", description="Local Web Interface for Pocket TTS")

# Ensure temp directory exists
CLONED_VOICES_DIR = ".tmp/cloned_voices"
os.makedirs(CLONED_VOICES_DIR, exist_ok=True)

# --- AUTH SETUP ---
# Attempt to read token from .env and login explicitly
HF_TOKEN = None
try:
    if os.path.exists(".env"):
        logger.info("Parsing .env for HF_TOKEN...")
        with open(".env", "r") as f:
            for line in f:
                if line.strip().startswith("HF_TOKEN="):
                    # Robust parsing to remove spaces/newlines/quotes
                    raw_val = line.strip().split("=", 1)[1]
                    HF_TOKEN = raw_val.strip().strip('"').strip("'")
                    if HF_TOKEN:
                        logger.info(f"Found HF_TOKEN (length: {len(HF_TOKEN)}). Logging in...")
                        try:
                            huggingface_hub.login(token=HF_TOKEN)
                            logger.info("Hugging Face Login: SUCCESS")
                        except Exception as login_err:
                            logger.error(f"Hugging Face Login Failed: {login_err}")
                    break
    if not HF_TOKEN:
        logger.warning("No HF_TOKEN found in .env. Falling back to cached credentials.")
except Exception as e:
    logger.error(f"Error during auth setup: {e}")

# Global model state
tts_model = None
model_loading = False

APP_VERSION = "1.1.0"

def get_model():
    global tts_model, model_loading
    if tts_model is None:
        if model_loading:
             # Simple wait mechanism if multiple requests hit during load
            while model_loading:
                time.sleep(0.5)
            return tts_model
            
        model_loading = True
        logger.info("Loading Pocket TTS model... This might take a moment.")
        try:
            tts_model = TTSModel.load_model()
            logger.info("Pocket TTS model loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            model_loading = False
            raise e
        finally:
            model_loading = False
    return tts_model

# --- API Endpoints ---

@app.get("/api/health")
def health_check():
    """Returns app version and auth status debugging info."""
    auth_status = "Unknown"
    token_preview = "None"
    try:
        from huggingface_hub import get_token
        token = get_token()
        if token:
            auth_status = "Logged In"
            token_preview = f"{token[:4]}...{token[-4:]}"
        else:
            auth_status = "Not Logged In (Token missing)"
    except Exception as e:
        auth_status = f"Error checking auth: {str(e)}"
        
    return {
        "status": "online",
        "version": APP_VERSION,
        "auth_status": auth_status,
        "token_preview": token_preview,
        "env_file_found": os.path.exists(".env")
    }

@app.get("/api/voices")
def list_voices():
    """Returns a list of available voices."""
    # Hardcoded list based on documentation
    voices = [
        {"id": "alba", "name": "Alba (Casual)"},
        {"id": "marius", "name": "Marius (Selfie)"},
        {"id": "javert", "name": "Javert (Butter)"},
        {"id": "jean", "name": "Jean (Freeform)"},
        {"id": "fantine", "name": "Fantine (VCTK)"},
        {"id": "cosette", "name": "Cosette (Expresso)"},
        {"id": "eponine", "name": "Eponine (VCTK)"},
        {"id": "azelma", "name": "Azelma (VCTK)"}
    ]
    return {"voices": voices}

@app.post("/api/generate")
async def generate_audio(
    text: str = Form(...),
    voice: str = Form("alba"),
    file: UploadFile = File(None)
):
    """Generates audio from text, supporting both preset voices and custom file uploads."""
    if not text:
        raise HTTPException(status_code=400, detail="Text is required")

    try:
        model = get_model()
        
        voice_target = voice
        
        # Handle file upload for cloning
        if file:
            logger.info(f"Processing uploaded voice file: {file.filename}")
            file_path = os.path.join(CLONED_VOICES_DIR, file.filename)
            
            # Save the uploaded file
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            voice_target = file_path
            logger.info(f"Using cloned voice from: {voice_target}")
        else:
             logger.info(f"Using preset voice: {voice_target}")

        
        # Get voice state
        try:
            voice_state = model.get_state_for_audio_prompt(voice_target)
        except Exception as e:
            logger.error(f"Error loading voice '{voice_target}': {e}")
            
            # AGGRESSIVE RETRY FOR AUTH ISSUES
            # If the error looks like the specific auth error, try logging in again right here
            if "voice cloning" in str(e) or "terms" in str(e) or "download" in str(e):
                logger.warning("Encountered auth error. Attempting emergency re-login...")
                try:
                    if os.path.exists(".env"):
                        with open(".env", "r") as f:
                            for line in f:
                                if line.strip().startswith("HF_TOKEN="):
                                    token = line.strip().split("=", 1)[1]
                                    huggingface_hub.login(token=token)
                                    logger.info("Emergency re-login successful. Retrying voice load...")
                                    # Retry loading state
                                    voice_state = model.get_state_for_audio_prompt(voice_target)
                                    break
                except Exception as retry_err:
                    logger.error(f"Emergency re-login failed: {retry_err}")
                    # Re-raise the original error if retry fails
                    raise HTTPException(status_code=400, detail=f"Failed to load voice. Your Hugging Face token might be invalid or you haven't accepted the terms. Error: {str(e)}")
            else:
                 raise HTTPException(status_code=400, detail=f"Failed to load voice. Error: {str(e)}")

        # Generate audio
        # audio is a 1D torch tensor
        audio_tensor = model.generate_audio(voice_state, text)
        
        # Convert to numpy
        audio_data = audio_tensor.numpy()
        
        # Create in-memory WAV file
        buffer = io.BytesIO()
        scipy.io.wavfile.write(buffer, model.sample_rate, audio_data)
        buffer.seek(0)
        
        # Clean up uploaded file if strictly necessary, but keeping it for now might be useful for debug
        # if file:
        #    os.remove(voice_target)
        
        return Response(content=buffer.read(), media_type="audio/wav")

    except Exception as e:
        logger.error(f"Generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Mount static files *after* API routes to avoid masking them
# We'll create the static directory in the next step
app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    # Use 8543 to avoid conflicts with ComfyUI/standard web apps
    uvicorn.run(app, host="0.0.0.0", port=8543)
