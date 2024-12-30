import glob
import os
from music_analysis import analyse_song
from utils import get_uuid
from config import STAGING_DIR, valid_extensions
import hashlib


def update_library():
    # check for files inside Staging
    staging_files = [
        f
        for f in os.listdir(STAGING_DIR)
        if os.path.isfile(os.path.join(STAGING_DIR, f))
        and any(f.lower().endswith(ext.lower()) for ext in valid_extensions)
    ]

    # for each file in the list of acceptable formats inside Staging...
    for file in staging_files:
        print(file)
        file_path = STAGING_DIR / file

        # compute the sha256 hash
        with open(file_path, "rb", buffering=0) as f:
            file_hash = hashlib.file_digest(f, "sha256").hexdigest()
            # TODO: check if the hash exists in the DB
            # TODO: if it does exist, log and ignore

        # compute a UUID for the song
        song_uuid = get_uuid()

        # analyze the song for features
        song_features = analyse_song(file_path)

        # TODO: extract song name if possible from mp3 tags, otherwise use the filename
        # TODO: extract all song metadata: artists, album, album art, release dates etc.
        # TODO: push all information to the DB (including the hash)
        # TODO: create a folder with name as GUID
        # TODO: rename song file - add GUID to the beginning
        # TODO: move the song file to the GUID folder
        # TODO: run ffmpeg and split the file for HSL steaming purposes


update_library()
