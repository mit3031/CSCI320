import datetime

from flask import Blueprint, redirect, request, url_for
from flask_login import login_required, current_user
from .db import get_db

bp = Blueprint("play", __name__, url_prefix="/play")

@bp.route("/song/<int:song_id>", methods=["POST"])
@login_required
def play_song(song_id: int):
    print(request.form)
    next_url = request.form['next']
    curr_time = datetime.datetime.now()

    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO listentosong (username, song_id, datetime_listened)
            VALUES (%s, %s, %s)
        """, (current_user.id, song_id, curr_time))
    
    conn.commit()

    if next_url:
        return(redirect(next_url))

@bp.route("/collection/<int:cid>", methods=["POST"])
@login_required
def play_collection(cid: int):
    next_url = request.form['next']
    curr_time = datetime.datetime.now()

    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO listentosong (song_id, username, datetime_listened)
            SELECT song_id, %s, %s
            FROM ispartofcollection
            WHERE collection_id = %s
        """, (current_user.id, curr_time, cid))
    
    conn.commit()

    if next_url:
        return(redirect(next_url))