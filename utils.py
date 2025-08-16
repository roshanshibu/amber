import hashlib
import uuid

import requests
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


def get_acoustic_id_info(ACOUSTID_API_KEY, fingerprint, duration):
    acousticid_url = f"https://api.acoustid.org/v2/lookup?client={ACOUSTID_API_KEY}&meta=recordings+releasegroups&fingerprint={fingerprint}&duration={duration}"
    response = requests.request("GET", acousticid_url)
    acousticid_response = response.json()
    try:
        recording = acousticid_response["results"][0]["recordings"][0]
        artists = [artist["name"] for artist in recording["artists"]]
        songName = recording["title"]
        recordingID = recording["id"]
        albumName = recording["releasegroups"][0]["title"]
        isSingle = recording["releasegroups"][0]["type"] == "Single"
        if isSingle:
            albumName += " - Single"
        return {
            "song": songName,
            "artists": artists,
            "recordingID": recordingID,
            "albumName": albumName,
            "isSingle": isSingle,
        }
    except Exception as e:
        print(str(e))
        return None


def get_musicbrainz_releaseID(recordingID):
    musicbrainz_url = (
        f"https://musicbrainz.org/ws/2/recording/{recordingID}?inc=releases&fmt=json"
    )
    response = requests.request(
        "GET",
        musicbrainz_url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:141.0) Gecko/20100101 Firefox/141.0"
        },
    )
    musicbrainz_response = response.json()
    try:
        releaseID = musicbrainz_response["releases"][0]["id"]
        return releaseID
    except Exception as e:
        print(str(e))
        return None


def get_album_art_url(musicbrainzReleaseID):
    coverart_url = f"http://coverartarchive.org/release/{musicbrainzReleaseID}"
    response = requests.request("GET", coverart_url)
    coverart_response = response.json()
    try:
        return coverart_response["images"][0]["thumbnails"]["large"]
    except Exception as e:
        print(str(e))
        return None
