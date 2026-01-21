import os
import huggingface_hub

# 1. Check .env directly
print("Checking .env content (masked)...")
try:
    if os.path.exists(".env"):
        with open(".env", "r") as f:
            for line in f:
                if "HF_TOKEN" in line:
                    parts = line.split("=")
                    if len(parts) > 1:
                         val = parts[1].strip()
                         print(f"Found HF_TOKEN. Length: {len(val)}")
                         print(f"First 4 chars: {val[:4]}")
                         print(f"Last 4 chars: {val[-4:]}")
                         import sys
                         print(f"Repr: {repr(val)}") # Check for hidden chars
                    else:
                        print("HF_TOKEN found but empty value.")
    else:
        print("No .env file found.")
except Exception as e:
    print(f"Error reading .env: {e}")

# 2. explicit login test
print("\nAttempting explicit login using .env value...")
try:
    if os.path.exists(".env"):
        with open(".env", "r") as f:
            for line in f:
                if line.strip().startswith("HF_TOKEN="):
                    raw_val = line.strip().split("=", 1)[1]
                    token = raw_val.strip().strip('"').strip("'")
                    huggingface_hub.login(token=token)
                    print("Explict login SUCCESS")
except Exception as e:
    print(f"Explicit login FAILED: {e}")
