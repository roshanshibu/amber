import hashlib
import time
import uuid

import requests
from config import MUSIC_DIR
from db import is_uuid_valid
from mutagen import File
from io import BytesIO
from PIL import Image


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


def get_recordings_from_fingerprint(ACOUSTID_API_KEY, fingerprint, duration, fetchAll):
    acousticid_url = f"https://api.acoustid.org/v2/lookup?client={ACOUSTID_API_KEY}&meta=recordings+releasegroups&fingerprint={fingerprint}&duration={duration}"
    response = requests.request("GET", acousticid_url)
    acousticid_response = response.json()
    try:
        allRecordings = acousticid_response["results"][0]["recordings"]
        res = []
        for recording in allRecordings:
            artists = [artist["name"] for artist in recording["artists"]]
            songName = recording["title"]
            recordingID = recording["id"]
            albumName = recording["releasegroups"][0]["title"]
            isSingle = recording["releasegroups"][0]["type"] == "Single"
            if isSingle:
                albumName += " - Single"
            res.append(
                {
                    "song": songName,
                    "artists": artists,
                    "recordingID": recordingID,
                    "albumName": albumName,
                    "isSingle": isSingle,
                }
            )
            if not fetchAll:
                break
        return res
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
        print("failed to get large thumbnail", str(e))
        return None


def add_album_art_urls_to_recordings(recordings):
    res = []
    for recording in recordings:
        final_album_art_url = None
        try:
            releaseID = get_musicbrainz_releaseID(recording["recordingID"])
            album_art_url = get_album_art_url(releaseID)
            final_album_art_url = get_final_url(album_art_url)
        except Exception as e:
            print(str(e))
        recording["albumArtURL"] = final_album_art_url
        res.append(recording)
    return res


def get_final_url(url):
    try:
        response = requests.get(url, allow_redirects=True, timeout=10)
        return response.url
    except requests.RequestException as e:
        print(f"Error: {e}")
        return None


def download_album_art(new_image_url, uuid):
    album_art_path = MUSIC_DIR / uuid / f"{uuid}.png"
    print("downloading new album art", new_image_url, uuid)
    response = requests.get(new_image_url)
    if response.status_code == 200:
        img = Image.open(BytesIO(response.content))

        if album_art_path.exists():
            timestamp = int(time.time())
            new_name = f"{album_art_path.stem}_{timestamp}{album_art_path.suffix}"
            album_art_path.rename(album_art_path.parent / new_name)
            print(f"Existing album art renamed to {new_name}")

        img.convert("RGB").save(album_art_path, "PNG")
        print(f"New image saved as {album_art_path}")
        return True
    return False
