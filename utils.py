import hashlib
import uuid
from db import is_uuid_valid
from mutagen import File
from io import BytesIO


def get_uuid():
    uhex = uuid.uuid4().hex
    snippet = uhex[:8]
    if is_uuid_valid(snippet):
        return snippet


def calculate_file_digest(file_path, hash_algo="sha256"):
    hasher = hashlib.new(hash_algo)
    with open(file_path, "rb") as f:
        while chunk := f.read(8192):
            hasher.update(chunk)
    return hasher.hexdigest()


def get_mp3_tags(file_path):
    audio = File(file_path)

    processed_tags = {
        "name": file_path.stem,
        "artists": None,
        "album": None,
        "cover_art": None,
    }

    if not audio or not audio.tags:
        return processed_tags

    tags = audio.tags.items()
    for key, value in tags:
        if key == "TIT2":
            processed_tags["name"] = value.text[0]
        elif key == "TPE1":
            processed_tags["artists"] = value.text[0]
        elif key == "TALB":
            processed_tags["album"] = value.text[0]
        elif key.startswith("APIC"):
            processed_tags["cover_art"] = BytesIO(value.data)
        # TODO: extract Genre information if available

    return processed_tags
