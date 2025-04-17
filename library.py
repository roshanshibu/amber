import os
from pathlib import Path
from fingerprint import get_audio_fingerprint
from db import init_db, insert_song_features, insert_song_info, is_duplicate_file
from music_analysis import analyse_song
from utils import calculate_file_digest, get_mp3_tags, get_uuid
from config import STAGING_DIR, MUSIC_DIR, valid_extensions
from PIL import Image


def init():
    init_db()
    try:
        os.makedirs(STAGING_DIR, exist_ok=True)
        os.makedirs(MUSIC_DIR, exist_ok=True)
    except OSError:
        print(f"Error creating staging and music directories")


def update_library():
    init()
    # check for files inside Staging
    staging_files = [
        f
        for f in os.listdir(STAGING_DIR)
        if os.path.isfile(os.path.join(STAGING_DIR, f))
        and any(f.lower().endswith(ext.lower()) for ext in valid_extensions)
    ]

    # for each file in the list of acceptable formats inside Staging...
    for file in staging_files:
        print(f"\n Processing {file} {'-' * 80}")
        file_path = STAGING_DIR / file

        # compute the sha256 hash
        file_hash = ""
        file_hash = calculate_file_digest(file_path)
        if is_duplicate_file(file_hash):
            print("Duplicate file! Skipping...")
            continue

        # compute a UUID for the song
        song_uuid = get_uuid()

        # analyze the song for features
        song_features = analyse_song(file_path)

        # extract all song metadata: song name (title), artists, album & album art
        tags = get_mp3_tags(file_path)

        # get the audio fingerprint and duration
        fingerprint, duration = get_audio_fingerprint(file_path)

        # push all information to the DB (including the hash)
        song_id = insert_song_info(
            song_uuid,
            tags["name"],
            tags["artists"],
            tags["album"],
            file_hash,
            fingerprint,
            duration,
        )
        insert_song_features(song_id, song_features)

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
            cover_art.save(song_folder / f"{song_uuid}.png", format="PNG")

        # run ffmpeg and split the file for HSL steaming purposes
        hls_split_command = f"""
                            ffmpeg -i "{song_folder / file}"                                \
                            -map 0:a -c:a aac -b:a 128k                                     \
                            -hls_time 5 -hls_list_size 0                                    \
                            -hls_segment_filename {song_folder / song_uuid}_%03d.ts         \
                            -f hls {song_folder / song_uuid}.m3u8                           \
                            -hide_banner -loglevel error
                            """
        os.system(hls_split_command)