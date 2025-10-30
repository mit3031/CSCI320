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
        RETURNING collection_id, name, creator_username;
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

def get_collection_tracks(collection_id: int) -> list:
    sql = """
        SELECT c.collection_id as cid,
        c.name AS collection_name,
        s.song_id AS song_id,
        s.title AS song_title,
        a.artist_id AS artist_id,
        a.name AS artist,
        ab.album_id AS album_id,
        ab.name AS album,
        s.length AS length
    FROM collection c
    JOIN ispartofcollection ipc ON c.collection_id = ipc.collection_id
    JOIN song s ON ipc.song_id = s.song_id
    JOIN makesong ms ON s.song_id = ms.song_id
    JOIN artist a ON ms.artist_id = a.artist_id
    JOIN ispartofalbum ipa ON ipa.song_id = s.song_id
    JOIN album ab ON ab.album_id = ipa.album_id
    WHERE c.collection_id = %s;
    """
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute(sql, (collection_id,))
        rows = cur.fetchall()
    
    return [{
        "cid": r[0],
        "collection_name": r[1],
        "song_id": r[2],
        "song": r[3],
        "artist_id": r[4],
        "artist": r[5],
        "album_id": r[6],
        "album": r[7],
        "length": r[8],
    } for r in rows]

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