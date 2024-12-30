import uuid
from mutagen import File
from io import BytesIO


def get_uuid():
    uhex = uuid.uuid4().hex
    snippet = "a" + uhex[:7]
    # TODO: Validate uniqueness of the uuid against the db
    return snippet


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
            processed_tags["name"] = value.text
        elif key == "TPE1":
            processed_tags["artists"] = value.text
        elif key == "TALB":
            processed_tags["album"] = value.text
        elif key.startswith("APIC"):
            processed_tags["cover_art"] = BytesIO(value.data)

    return processed_tags
