from ..db import get_db

# ----- CREATE ---------------------------------------------------------------
def create_collection(name: str, creator_username: str) -> dict:
    sql = """
        INSERT INTO collection (name, creator_username)
        VALUES (%s, %s)
        RETURNING collection_id, name, creator_username;
    """
    conn = get_db()
    with conn:
        with conn.cursor() as cur:
            cur.execute(sql, (name, creator_username))
            row = cur.fetchone()
    return {
        "collection_id": row[0],
        "name": row[1],
        "creator_username": row[2],
    }

# ----- READ -----------------------------------------------------------------
def view_collections() -> list[dict]:
    sql = """
        SELECT collection_id, name, creator_username
        FROM collection
        ORDER BY name ASC;
    """
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute(sql)
        rows = cur.fetchall()
    return [
        {"collection_id": r[0], "name": r[1], "creator_username": r[2]}
        for r in rows
    ]

