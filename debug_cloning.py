import os
import shutil
import logging
from pocket_tts import TTSModel
import huggingface_hub

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Authentication
try:
    if os.path.exists(".env"):
        print("Found .env, looking for token...")
        with open(".env", "r") as f:
            for line in f:
                if line.strip().startswith("HF_TOKEN="):
                    token = line.strip().split("=", 1)[1]
                    if token:
                        print(f"Logging in with token: {token[:4]}...{token[-4:]}")
                        huggingface_hub.login(token=token)
                        break
    else:
        print("No .env found!")
except Exception as e:
    print(f"Auth failed: {e}")

# Dummy clone setup
CLONE_FILE = ".tmp/debug_voice.wav"
# Create a dummy wav file if it doesn't exist just to test the loading phase
import scipy.io.wavfile
import numpy as np
if not os.path.exists(CLONE_FILE):
    samplerate = 44100; fs = 100
    t = np.linspace(0., 1., samplerate)
    amplitude = np.iinfo(np.int16).max
    data = amplitude * np.sin(2. * np.pi * fs * t)
    scipy.io.wavfile.write(CLONE_FILE, samplerate, data.astype(np.int16))

try:
    print("Loading model...")
    tts = TTSModel.load_model()
    print("Model loaded.")

    print(f"Attempting to load custom voice from {CLONE_FILE}...")
    # This is the line that triggers the download/auth check for the cloning module
    voice_state = tts.get_state_for_audio_prompt(CLONE_FILE)
    print("SUCCESS: Voice state loaded!")
    
    print("Generating...")
    tts.generate_audio(voice_state, "Test generation.")
    print("SUCCESS: Generation complete!")

except Exception as e:
    print("\n------------------------------------------------")
    print("FAILURE REPRODUCTION")
    print(f"Error Type: {type(e).__name__}")
    print(f"Error Message: {e}")
    print("------------------------------------------------\n")
    import traceback
    traceback.print_exc()
