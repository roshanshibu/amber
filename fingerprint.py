import subprocess
from config import BASE_DIR
import requests
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv("ACOUSTID_API_KEY")


def get_audio_fingerprint(file_path):
    """Generate fingerprint and duration using fpcalc."""
    fpcalc_path = BASE_DIR / "bin" / "fpcalc"
    result = subprocess.run([fpcalc_path, file_path], capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"fpcalc error: {result.stderr.strip()}")
    output = {
        line.split("=", 1)[0]: line.split("=", 1)[1]
        for line in result.stdout.splitlines()
    }
    return output["FINGERPRINT"], int(output["DURATION"])
