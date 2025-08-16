from flask import Flask, request
from flask_cors import CORS
from dotenv import load_dotenv
import os
from db import (
    full_search,
    get_random_song_uuid_list,
    get_song_details,
    get_song_fingerprint_and_duration,
)
from library import update_library
from utils import get_acoustic_id_info, get_album_art_url, get_musicbrainz_releaseID

app = Flask(__name__)
CORS(app)

load_dotenv()
DUMMY_TOKEN = os.getenv("AMBER_DUMMY_TOKEN")
ACOUSTID_API_KEY = os.getenv("ACOUSTID_API_KEY")


def token_required(f):
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token or token != DUMMY_TOKEN:
            return "Unauthorized", 401
        return f(*args, **kwargs)

    decorated.__name__ = f.__name__
    return decorated


@app.route("/dummyAuth", methods=["GET"])
def dummyAuth():
    if request.method == "GET":
        session_token = request.headers.get("Authorization")
        if not session_token:
            return "Missing token", 400
        if session_token == DUMMY_TOKEN:
            return "Authenticated", 200
        else:
            return "Unauthorized: Invalid token", 401


@app.route("/updateLibrary", methods=["GET"])
@token_required
def updateLibrary():
    update_library()
    return "Library updated", 200


@app.route("/songDetails", methods=["GET"])
@token_required
def songDetails():
    if request.method == "GET":
        uuid = request.args.get("UUID")
        if not uuid:
            return "Malformed request", 400
        else:
            songDetails = get_song_details(uuid)
            if songDetails is not None:
                return songDetails, 200
            else:
                return "Song not found", 400


@app.route("/randomPlaylist", methods=["GET"])
@token_required
def randomPlaylist():
    if request.method == "GET":
        playlist_length = request.args.get("length") or "10"
        if playlist_length.isnumeric():
            playlist_length = int(playlist_length)
        else:
            playlist_length = 10
        playlist = get_random_song_uuid_list(playlist_length)
        return {"playlist": playlist}, 200


@app.route("/search", methods=["GET"])
@token_required
def search():
    if request.method == "GET":
        term = request.args.get("term")
        if not term:
            return "Malformed request", 400
        elif len(term.replace(" ", "")) <= 3:
            return "Include atleast 4 characters in search query", 400
        else:
            return {"results": full_search(term)}, 200


@app.route("/getMetadata", methods=["GET"])
@token_required
def freshMetadata():
    if request.method == "GET":
        uuid = request.args.get("UUID")
        acousticid_data = get_song_fingerprint_and_duration(uuid)
        duration = acousticid_data["duration"]
        fingerprint = acousticid_data["fingerprint"]
        # get song text metadata
        acoustic_id_info = get_acoustic_id_info(ACOUSTID_API_KEY, fingerprint, duration)
        if acoustic_id_info is None:
            return "Error getting acoustic id data", 500
        # get album art
        musicbrainz_releaseID = get_musicbrainz_releaseID(
            acoustic_id_info["recordingID"]
        )
        album_art_url = None
        if musicbrainz_releaseID is not None:
            album_art_url = get_album_art_url(musicbrainz_releaseID)
        return {
            "albumName": acoustic_id_info["albumName"],
            "artists": acoustic_id_info["artists"],
            "song": acoustic_id_info["song"],
            "albumart": album_art_url,
        }, 200


@app.route("/replaceMetadata", methods=["POST"])
@token_required
def replaceMetadata():
    if request.method == "POST":
        uuid = request.args.get("UUID")
        albumName = request.args.get("albumName")
        artistsUnsafe = request.args.get("artistsUnsafe")
        songName = request.args.get("songName")
        albumArtURL = request.args.get("albumArtURL")
        return "not implemented", 200


if __name__ == "__main__":
    app.run(debug=True)
