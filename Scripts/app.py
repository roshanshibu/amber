import os
from pathlib import Path
from music_analysis import analyse_song
from utils import get_mp3_tags, get_uuid
from config import STAGING_DIR, MUSIC_DIR, valid_extensions
import hashlib
from PIL import Image


def init():
    try:
        os.makedirs(STAGING_DIR, exist_ok=True)
        os.makedirs(MUSIC_DIR, exist_ok=True)
    except OSError:
        print(f"Error creating staging and music directories")


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
        print(f"\n{file} {'-' * 80}")
        file_path = STAGING_DIR / file

        # compute the sha256 hash
        with open(file_path, "rb", buffering=0) as f:
            file_hash = hashlib.file_digest(f, "sha256").hexdigest()
            # TODO: check if the hash exists in the DB
            # TODO: if it does exist, log and ignore

        # compute a UUID for the song
        song_uuid = get_uuid()

        # analyze the song for features
        # song_features = analyse_song(file_path)

        # extract all song metadata: song name (title), artists, album & album art
        tags = get_mp3_tags(file_path)

        # TODO: push all information to the DB (including the hash)

        # create a folder with name as song_uuid in Music folder
        song_folder = MUSIC_DIR / song_uuid
        Path(song_folder).mkdir(parents=True, exist_ok=False)

        # rename song file - add song_uuid to the beginning, and move it to the song_uuid folder
        os.rename(file_path, song_folder / file)

        # if album art exists, write it to uuid.png
        if tags["cover_art"]:
            try:
                cover_art = Image.open(tags["cover_art"])
            except Exception as e:
                return

            # Save as PNG, ignoring original image format
            cover_art.save(song_folder / f"{song_uuid}.png", format="PNG")

        # run ffmpeg and split the file for HSL steaming purposes
        hls_split_command = f'ffmpeg -i "{song_folder / file}" -map 0:a -c:a aac -b:a 128k -hls_time 5 -hls_list_size 0 -hls_segment_filename {song_folder / song_uuid}_%03d.ts -f hls {song_folder / song_uuid}.m3u8'
        os.system(hls_split_command)


init()
update_library()
