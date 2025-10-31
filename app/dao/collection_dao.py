from ..db import get_db

# ----- CREATE ---------------------------------------------------------------
def create_collection(name: str, creator_username: str):
    sql = """
        INSERT INTO collection (name, creator_username)
        VALUES (%s, %s)
    """
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute(sql, (name, creator_username))
    
    conn.commit()

# ----- READ -----------------------------------------------------------------
def view_collections(creator_username: str) -> list[dict]:
    sql = """
        SELECT collection_id, name, creator_username
        FROM collection
        WHERE creator_username = %s
        ORDER BY name ASC;
    """
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute(sql, (creator_username,))
        rows = cur.fetchall()

    return [
        {"collection_id": r[0], "name": r[1], "creator_username": r[2]}
        for r in rows
    ]

# ----- RENAME -----------------------------------------------------------------
def rename_collection(collection_id: int, new_name: str) -> dict | None:
    sql = """
        UPDATE collection
        SET name = %s
        WHERE collection_id = %s
    """
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute(sql, (new_name, collection_id))

    conn.commit()

# ----- DELETE ---------------------------------------------------------------
def delete_collection(collection_id: int):
    sql = "DELETE FROM collection WHERE collection_id = %s;"
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute(sql, (collection_id,))

    conn.commit()

def get_collection_tracks(username: str, collection_id: int) -> list:
    sql = """
    SELECT c.collection_id as cid,
        c.name AS collection_name,
        s.song_id AS song_id,
        s.title AS song_title,
        a.artist_id AS artist_id,
        a.name AS artist,
        ab.album_id AS album_id,
        ab.name AS album,
        s.length AS length,
        g.name AS genre
    FROM collection c
    LEFT OUTER JOIN ispartofcollection ipc ON c.collection_id = ipc.collection_id
    LEFT OUTER JOIN song s ON ipc.song_id = s.song_id
    LEFT OUTER JOIN makesong ms ON s.song_id = ms.song_id
    LEFT OUTER JOIN artist a ON ms.artist_id = a.artist_id
    LEFT OUTER JOIN ispartofalbum ipa ON ipa.song_id = s.song_id
    LEFT OUTER JOIN album ab ON ab.album_id = ipa.album_id
    LEFT OUTER JOIN songhasgenre shg ON shg.song_id = s.song_id
    LEFT OUTER JOIN genre g ON g.genre_id = shg.genre_id
    WHERE c.collection_id = %s;
    """

    song_ids = []
    results = []

    conn = get_db()
    with conn.cursor() as cur:
        cur.execute(sql, (collection_id,))
        rows = cur.fetchall()

        for song in rows:
            if song[2] not in song_ids:
                cur.execute("""
                    SELECT COUNT(*)
                    FROM listentosong
                    WHERE username = %s AND song_id = %s
                """, (username, song[2]))

                listens = cur.fetchone()
                if listens is None:
                    listens = 0
                else:
                    listens = listens[0]

                song_ids.append(song[2])
                results.append({
                    "cid": song[0],
                    "collection_name": song[1],
                    "song_id": song[2],
                    "song": song[3],
                    "artist_id": [song[4]],
                    "artist": [song[5]],
                    "album_id": [song[6]],
                    "album": [song[7]],
                    "length": song[8],
                    "genre": [song[9]],
                    "listens": listens,
                })
            else:
                print(results)
                idx = song_ids.index(song[2])

                if song[4] not in results[idx]["artist_id"]:
                    results[idx]["artist_id"].append(song[4])
                    results[idx]["artist"].append(song[5])
                if song[6] not in results[idx]["album_id"]:
                    results[idx]["album_id"].append(song[6])
                    results[idx]["album"].append(song[7])
                if song[9] not in results[idx]["genre"]:
                    results[idx]["genre"].append(song[9])

    return results

    """
    collections = [{
        "cid": r[0],
        "collection_name": r[1],
        "song_id": r[2],
        "song": r[3],
        "artist_id": r[4],
        "artist": r[5],
        "album_id": r[6],
        "album": r[7],
        "length": r[8],
        "genre": r[9],
    } for r in rows]
    print(rows)

    return collections
    """

def get_collection_info(collection_id: int):
    sql = """
    SELECT COUNT(s.song_id) as num_song, SUM(s.length) as tot_length
    FROM ispartofcollection ipc
    JOIN song s ON ipc.song_id = s.song_id
    WHERE ipc.collection_id = %s
    """
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute(sql, (collection_id,))
        row = cur.fetchone()
    
    return row

def get_track_info(song_id: int) -> list[dict]:
    sql = """
        SELECT title, release_date, length, is_explicit
        FROM song
        WHERE song_id = %s
    """

    conn = get_db()
    with conn.cursor() as cur:
        cur.execute(sql, (song_id,))
        rows = cur.fetchall()
    
    return [{
        'title': r[0],
        'release_date': r[1],
        'length': r[2],
        'is_explicit': r[4],
    } for r in rows]

def remove_song_from_collection(collection_id: int, song_id: int):
    sql = """
    DELETE FROM ispartofcollection 
    WHERE collection_id = %s AND song_id = %s;
    """

    print(collection_id, song_id)
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute(sql, (collection_id, song_id))

    conn.commit()
    
def remove_album_from_collection(collection_id: int, album_name: str):
    sql = """
    DELETE FROM ispartofcollection
    WHERE collection_id = %s
        AND song_id IN (
            SELECT ipa.song_id
            FROM ispartofalbum ipa
            JOIN album a on ipa.album_id = a.album_id
            WHERE a.name = %s
        );
    """

    conn = get_db()
    with conn.cursor() as cur:
        cur.execute(sql, (collection_id, album_name))

    conn.commit()

def add_album_to_collection(collection_id: int, album_name: str):
    sql = """
    INSERT INTO ispartofcollection
    WHERE collection_id = %s 
        AND song_id in (
            SELECT
        );
    """

    conn = get_db()
    with conn.cursor() as cur:
        cur.execute(sql, (collection_id, album_name))

    conn.commit()