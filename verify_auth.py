import os
from huggingface_hub import login, hf_hub_download
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

REPO_ID = "kyutai/pocket-tts"
FILENAME = "config.json" # Just a small file to check access

def check_access():
    print(f"Checking access to {REPO_ID}...")
    try:
        # Try without explicit token first (uses cache)
        path = hf_hub_download(repo_id=REPO_ID, filename=FILENAME)
        print(f"[SUCCESS] Successfully accessed {REPO_ID}. File downloaded to: {path}")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to access repo: {e}")
        return False

if __name__ == "__main__":
    if check_access():
        print("\nAuth seems fine. The app should work if it picks up the same environment.")
    else:
        print("\nAuth check failed.")
        
        # Try reading token from .env if it exists
        if os.path.exists(".env"):
            print("Found .env file. Checking for HF_TOKEN...")
            with open(".env", "r") as f:
                for line in f:
                    if line.startswith("HF_TOKEN="):
                        token = line.strip().split("=", 1)[1]
                        if token:
                            print("Found token in .env. Attempting login...")
                            try:
                                login(token=token)
                                check_access()
                            except Exception as e:
                                print(f"Login with .env token failed: {e}")
