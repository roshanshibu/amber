import numbers
import sqlite3
from config import DB_PATH


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS Songs
            (
                ID INTEGER NOT NULL PRIMARY KEY,
                UUID TEXT UNIQUE,
                Name TEXT,
                UnsafeArtists TEXT,
                Album TEXT,
                Hash TEXT,
                Fingerprint TEXT,
                Duration INT
            )"""
    )
    conn.commit()
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS Artists
            (
                ID INTEGER NOT NULL PRIMARY KEY,
                Name TEXT
            )"""
    )
    conn.commit()
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS SongArtistMap
            (
                SongID INT,
                ArtistID INT,
                FOREIGN KEY(SongID) REFERENCES Songs(ID),
                FOREIGN KEY(ArtistID) REFERENCES Artists(ID)
            )"""
    )
    conn.commit()
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS Features
            (
                SongID INT UNIQUE,
                tempo REAL, onset_strength_mean REAL, onset_strength_std REAL, 
                spectral_centroid REAL, spectral_bandwidth REAL, spectral_rolloff REAL, spectral_flatness REAL, 
                rms_energy REAL, zcr REAL,
                FOREIGN KEY(SongID) REFERENCES Songs(ID)
            )"""
    )
    conn.commit()
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS UserTags
            (
                ID INTEGER NOT NULL PRIMARY KEY,
                Name TEXT UNIQUE
            )"""
    )
    conn.commit()
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS SongUserTagMapping
            (
                SongID INT,
                UserTagID INT,
                FOREIGN KEY(SongID) REFERENCES Songs(ID),
                FOREIGN KEY(UserTagID) REFERENCES UserTags(ID)
            )"""
    )
    conn.commit()

    cursor.close()


def insert_song_info(uuid, name, artists, album, hash, fingerprint, duration):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO Songs (UUID, Name, UnsafeArtists,
                Album, Hash,
                Fingerprint, Duration) VALUES (?,?,?,?,?,?,?)""",
        (uuid, name, artists, album, hash, fingerprint, duration),
    )
    song_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return song_id


def insert_song_features(song_id, features):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """INSERT OR IGNORE INTO Features (SongID, 
                        tempo, onset_strength_mean, onset_strength_std, 
                        spectral_centroid, spectral_bandwidth, spectral_rolloff, spectral_flatness, 
                        rms_energy, zcr) VALUES (?,?,?,?,?,?,?,?,?,?)""",
        (
            song_id,
            float(features["temporal"]["tempo"]),
            float(features["temporal"]["onset_strength_mean"]),
            float(features["temporal"]["onset_strength_std"]),
            float(features["spectral"]["spectral_centroid"]),
            float(features["spectral"]["spectral_bandwidth"]),
            float(features["spectral"]["spectral_rolloff"]),
            float(features["spectral"]["spectral_flatness"]),
            float(features["energy"]["rms_energy"]),
            float(features["energy"]["zcr"]),
        ),
    )
    conn.commit()
    conn.close()


def is_value_unique(table_name, column_name, value):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            f"SELECT COUNT(*) FROM {table_name} WHERE {column_name}=?", (value,)
        )
        result = cursor.fetchone()[0]
        return result == 0
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    return False


def is_uuid_valid(new_uuid):
    # check if new_uuid does not exist in db
    return is_value_unique("Songs", "UUID", new_uuid)


def is_duplicate_file(hash):
    # check if the same file was processed earlier
    return not is_value_unique("Songs", "Hash", hash)


def get_random_song_uuid_list(list_length):
    try:
        if not isinstance(list_length, numbers.Number):
            print(f"List length has to be a number, got: '{list_length}'")
            return None

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            f"SELECT UUID, Name, UnsafeArtists, Album, Duration FROM Songs ORDER BY RANDOM() LIMIT {list_length}"
        )
        result = cursor.fetchall()
        response = []
        for hit in result:
            response.append(
                {
                    "UUID": hit[0],
                    "Name": hit[1],
                    "Artists": hit[2],
                    "Album": hit[3],
                    "Duration": hit[4],
                }
            )
        return response
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    return None


def get_random_song_uuid():
    return get_random_song_uuid_list(1)[0]


def get_song_details(uuid):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT ID, Name, UnsafeArtists, Album FROM Songs WHERE UUID=?", (uuid,)
        )
        result = cursor.fetchone()
        if result is not None:
            return {
                "uuid": uuid,
                "name": result[1],
                "artists": result[2],
                "album": result[3],
            }
        return None
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    return None


def get_song_fingerprint_and_duration(uuid):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT Fingerprint, Duration FROM Songs WHERE UUID=?", (uuid,))
        result = cursor.fetchone()
        if result is not None:
            return {"fingerprint": result[0], "duration": result[1]}
        return None
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    return False


def full_search(search_term):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        pattern = f"%{search_term.lower()}%"
        print(pattern)
        query = """
        SELECT UUID, Name, UnsafeArtists, Album, Duration
        FROM Songs
        WHERE LOWER(Name) LIKE ?
           OR LOWER(UnsafeArtists) LIKE ?
           OR LOWER(Album) LIKE ?
        LIMIT 50
        """
        cursor.execute(
            query,
            (pattern, pattern, pattern),
        )
        result = cursor.fetchall()
        response = []
        for hit in result:
            response.append(
                {
                    "UUID": hit[0],
                    "Name": hit[1],
                    "Artists": hit[2],
                    "Album": hit[3],
                    "Duration": hit[4],
                }
            )
        return response
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    return None
