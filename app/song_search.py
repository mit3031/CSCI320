#
# Implements the search queries for songs
# Author: Joseph Britton (jtb8595)
#

import psycopg

from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_login import login_required, login_user, logout_user, current_user
from .models import User
from .db import get_db
import datetime

bp = Blueprint("search", __name__, url_prefix="/search")

#
# Searches the database for songs that contain a search term in a given field
# "search_by" field should only ever be "name", "artist", "album", or "genre"
# Author: Joseph Britton (jtb8595)
#
@bp.route("/search", methods=["GET", "POST"])
@login_required
def search_songs():
    if request.method == "POST":
        search_term = request.form["search"].strip()  # Whatever's in the search bar
        search_by = request.form["search_by"].strip()  # Should be a dropdown
        user = current_user.id
    
        db_conn = get_db()
        try:
            with db_conn.cursor() as curs:
                if search_by == "name":
                    print(f"Searching for {search_term} in name")
                    curs.execute(
                        'SELECT DISTINCT so.song_id, so.title, ar.name, al.name, g.name AS genre, so.length, so.release_date '
                        'FROM "song" AS so '
                        'INNER JOIN "makesong" AS m ON (so.song_id = m.song_id) '
                        'INNER JOIN "artist" AS ar ON (ar.artist_id = m.artist_id) '
                        'INNER JOIN "ispartofalbum" AS i ON (so.song_id = i.song_id) '
                        'INNER JOIN "album" AS al ON (al.album_id = i.album_id) '
                        'LEFT JOIN "songhasgenre" AS shg ON (so.song_id = shg.song_id) '
                        'LEFT JOIN "genre" AS g ON (g.genre_id = shg.genre_id) '
                        f'WHERE (so.title LIKE \'%%{search_term}%%\') '
                        'ORDER BY so.title ASC, ar.name ASC',
                        []
                    )

                elif search_by == "artist":
                    print(f"Searching for {search_term} in artist")
                    curs.execute(
                        'SELECT DISTINCT so.song_id, so.title, ar.name, al.name, g.name AS genre, so.length, so.release_date '
                        'FROM "song" AS so '
                        'INNER JOIN "makesong" AS m ON (so.song_id = m.song_id) '
                        'INNER JOIN "artist" AS ar ON (ar.artist_id = m.artist_id) '
                        'INNER JOIN "ispartofalbum" AS i ON (so.song_id = i.song_id) '
                        'INNER JOIN "album" AS al ON (al.album_id = i.album_id) '
                        'LEFT JOIN "songhasgenre" AS shg ON (so.song_id = shg.song_id) '
                        'LEFT JOIN "genre" AS g ON (g.genre_id = shg.genre_id) '
                        f'WHERE ar.name LIKE \'%%{search_term}%%\' '
                        'ORDER BY so.title ASC, ar.name ASC',
                        []
                    )
            
                elif search_by == "album":
                    print(f"Searching for {search_term} in album")
                    curs.execute(
                        'SELECT DISTINCT so.song_id, so.title, ar.name, al.name, g.name AS genre, so.length, so.release_date '
                        'FROM "album" AS al '
                        'INNER JOIN "ispartofalbum" AS i ON (i.album_id = al.album_id) '
                        'INNER JOIN "song" AS so ON (so.song_id = i.song_id) '
                        'INNER JOIN "makesong" AS m ON (so.song_id = m.song_id) '
                        'INNER JOIN "artist" AS ar ON (ar.artist_id = m.artist_id) '
                        'LEFT JOIN "songhasgenre" AS shg ON (so.song_id = shg.song_id) '
                        'LEFT JOIN "genre" AS g ON (g.genre_id = shg.genre_id) '
                        f'WHERE al.name LIKE \'%%{search_term}%%\' '
                        'ORDER BY so.title ASC, ar.name ASC',
                        []
                    )

                elif search_by == "genre":
                    print(f"Searching for {search_term} in genre")
                    curs.execute(
                        'SELECT DISTINCT so.song_id, so.title, ar.name, al.name, g.name AS genre, so.length, so.release_date '
                        'FROM "genre" AS g '
                        'INNER JOIN "songhasgenre" AS h ON (h.genre_id = g.genre_id) '
                        'INNER JOIN "song" AS so ON (so.song_id = h.song_id) '
                        'INNER JOIN "makesong" AS m ON (so.song_id = m.song_id) '
                        'INNER JOIN "artist" AS ar ON (ar.artist_id = m.artist_id) '
                        'INNER JOIN "ispartofalbum" AS i ON (so.song_id = i.song_id) '
                        'INNER JOIN "album" AS al ON (i.album_id = al.album_id) '
                        f'WHERE g.name LIKE \'%%{search_term}%%\' '
                        'ORDER BY so.title ASC, ar.name ASC',
                        []
                    )
                
                # songs[x] = [song id, song name, artist, album, genre, song length, release_date]
                songs = curs.fetchall()
                song_ids = []
                results = []  # [name, artist, album, length, number of times listened]

                # Organize search results
                for song in songs:
                    # check if the song is not already in results
                    if song[0] not in song_ids:
                        # Not in results - add it

                        # Get times listened to song
                        curs.execute(
                            'SELECT COUNT(*) '
                            'FROM "listentosong" '
                            f'WHERE song_id = {song[0]}',
                            []
                        )

                        # Add song information to results
                        results.append({
                            "song_id": song[0],
                            "name": song[1], 
                            "artist": song[2], 
                            "album": song[3], 
                            "genre": song[4],
                            "length": song[5],
                            "release_date": song[6],
                            "listened": curs.fetchone()[0]
                        })
                        song_ids.append(song[0])
                    else:
                        toCheck = results[song_ids.index(song[0])]
                        # In results - add the artist to song information if not already there
                        if song[2] not in toCheck['artist']:
                            results[song_ids.index(song[0])]['artist'] += ", " + song[2]
                        # Do the same for album
                        if song[3] not in toCheck['album']:
                            results[song_ids.index(song[0])]['album'] += ", " + song[3]
                        # Do the same for genre
                        if song[4] and song[4] not in toCheck['genre']:
                            results[song_ids.index(song[0])]['genre'] += ", " + song[4]
            
                db_conn.commit()
        except psycopg.Error as e:
            db_conn.rollback()
            flash(f"Database error: {e}")
            return f"Database error: {e}", 500
    
        return render_template("search/results.html", results=results, search_term=search_term, search_by=search_by)

    return render_template("search/search.html")

"""
Allows users to sort their search results by song name, artist, genre, or year
Supports both ascending and descending order without retyping the search term
"""
@bp.route("/sort_songs", methods=["POST"])
@login_required
def sort_songs():
    sort_by = request.form.get("sort_by")
    direction = request.form.get("direction", "asc")
    search_term = request.form.get("search_term")
    search_by = request.form.get("search_by")

    db_conn = get_db()
    results = []

    sort_map = {
        "song_name": "so.title",
        "artist": "artist_names",
        "genre": "genre_names",
        "year": "so.release_date"
    }
    order_col = sort_map.get(sort_by, "so.title")
    order_dir = "ASC" if direction == "asc" else "DESC"

    alias_map = {
        "name": "so",
        "artist": "ar",
        "album": "al",
        "genre": "g"
    }
    search_alias = alias_map.get(search_by, "so")
    if search_alias == "so":
        search_col = "title"
    else:
        search_col = "name"

    try:
        with db_conn.cursor() as curs:
            query = f'''
                SELECT
                    so.song_id,
                    so.title,
                    STRING_AGG(DISTINCT ar.name, ', ') AS artist_names,
                    STRING_AGG(DISTINCT al.name, ', ') AS album_names,
                    STRING_AGG(DISTINCT g.name, ', ') AS genre_names,
                    so.length,
                    so.release_date
                FROM "song" AS so
                INNER JOIN "makesong" AS m ON so.song_id = m.song_id
                INNER JOIN "artist" AS ar ON ar.artist_id = m.artist_id
                INNER JOIN "ispartofalbum" AS i ON so.song_id = i.song_id
                INNER JOIN "album" AS al ON al.album_id = i.album_id
                LEFT JOIN "songhasgenre" AS h ON so.song_id = h.song_id
                LEFT JOIN "genre" AS g ON g.genre_id = h.genre_id
                WHERE {search_alias}.{search_col} ILIKE %s
                GROUP BY so.song_id, so.title, so.length, so.release_date
                ORDER BY {order_col} {order_dir}
            '''
            curs.execute(query, [f"%{search_term}%"])
            songs = curs.fetchall()

            for song in songs:
                curs.execute(
                    'SELECT COUNT(*) FROM "listentosong" WHERE username = %s AND song_id = %s',
                    [current_user.id, song[0]]
                )
                listens = curs.fetchone()[0]

                results.append({
                    "song_id": song[0],
                    "name": song[1],
                    "artist": song[2],
                    "album": song[3],
                    "genre": song[4] if song[4] else "—",
                    "length": song[5],
                    "release_date": song[6],
                    "listened": listens
                })

        db_conn.commit()

    except psycopg.Error as e:
        db_conn.rollback()
        flash(f"Database error: {e}")
        return f"Database error: {e}", 500

    return render_template("search/results.html", results=results, search_term=search_term, search_by=search_by)

"""
Handles song playback. When a user clicks Play, this route logs that
listening event in the listentosong table with the datetime and username
"""
@bp.route("/play/<int:song_id>", methods=["POST"]) # Based on Shu's code from play.py
@login_required
def play_song(song_id: int):
    curr_time = datetime.datetime.now()
    next_url = request.form.get("next")  

    db_conn = get_db()
    try:
        with db_conn.cursor() as curs:
            curs.execute("""
                INSERT INTO "listentosong" (username, song_id, datetime_listened)
                VALUES (%s, %s, %s)
            """, (current_user.id, song_id, curr_time))
        db_conn.commit()
    except Exception as e:
        db_conn.rollback()
        print(f"Database error while playing song: {e}")
        flash("Error logging play action.")
        return redirect(url_for("search.search_songs"))

    # Redirect back to previous page if provided
    if next_url:
        return redirect(next_url)
    return redirect(url_for("search.search_songs"))