from pathlib import Path

# Directories
BASE_DIR = Path(__file__).resolve().parents[0]
STAGING_DIR = BASE_DIR / "Staging"
MUSIC_DIR = BASE_DIR / "Music"
DB_PATH = BASE_DIR / "Amber.db"

valid_extensions = [".mp3"]
