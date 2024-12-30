from pathlib import Path

# Directories
BASE_DIR = Path(__file__).resolve().parents[1]
STAGING_DIR = BASE_DIR / "Staging"
MUSIC_DIR = BASE_DIR / "Music"

valid_extensions = [".mp3"]
