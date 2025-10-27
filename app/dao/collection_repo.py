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