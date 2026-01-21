import os
import io
import time
import logging
import scipy.io.wavfile
import numpy as np
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from pocket_tts import TTSModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="WebPocketTTS", description="Local Web Interface for Pocket TTS")

# Global model state
tts_model = None
model_loading = False

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

# --- Pydantic Models ---
class GenerateRequest(BaseModel):
    text: str
    voice: str = "alba"

# --- API Endpoints ---

@app.get("/api/voices")
def list_voices():
    """Returns a list of available voices."""
    # Hardcoded list based on documentation, as pocket-tts doesn't seem to have a dynamic list API exposed easily 
    # without deeper inspection. We can update this later.
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
async def generate_audio(request: GenerateRequest):
    """Generates audio from text."""
    if not request.text:
        raise HTTPException(status_code=400, detail="Text is required")

    try:
        model = get_model()
        
        logger.info(f"Generating audio for voice: {request.voice}")
        
        # Get voice state
        # Note: In a real app we might want to cache these states too if they are heavy
        try:
            voice_state = model.get_state_for_audio_prompt(request.voice)
        except Exception as e:
            logger.error(f"Error loading voice '{request.voice}': {e}")
             # Fallback to default if custom/specific voice fails, or error out
            raise HTTPException(status_code=400, detail=f"Voice '{request.voice}' not found or valid.")

        # Generate audio
        # audio is a 1D torch tensor
        audio_tensor = model.generate_audio(voice_state, request.text)
        
        # Convert to numpy
        audio_data = audio_tensor.numpy()
        
        # Create in-memory WAV file
        buffer = io.BytesIO()
        scipy.io.wavfile.write(buffer, model.sample_rate, audio_data)
        buffer.seek(0)
        
        return Response(content=buffer.read(), media_type="audio/wav")

    except Exception as e:
        logger.error(f"Generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Mount static files *after* API routes to avoid masking them
# We'll create the static directory in the next step
app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
