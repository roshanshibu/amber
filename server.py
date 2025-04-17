from flask import Flask, request
from flask_cors import CORS
from dotenv import load_dotenv
import os
from db import get_random_song_uuid, get_random_song_uuid_list, get_song_details
from library import update_library

app = Flask(__name__)
CORS(app)

load_dotenv()
DUMMY_TOKEN = os.getenv("AMBER_DUMMY_TOKEN")


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
        return {"uuids": playlist}, 200


if __name__ == "__main__":
    app.run(debug=True)
