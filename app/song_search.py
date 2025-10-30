#
# TO-DO: 
#   Finish search (remaining features listed in block comment)
#

#
# Implements the search queries for songs
# Author: Joseph Britton (jtb8595)
#

import psycopg
import bcrypt
import datetime
import time

from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_login import login_required, login_user, logout_user, current_user
from .models import User
from .db import get_db

bp = Blueprint("search", __name__, url_prefix="/search")

# Things left to implement:
#   Update SQL statements to include listen count when implemented
#   Rendering the results (should be implemented, unchecked due to new routing scrambling the flask)

#
# Searches the database for songs that contain a search term in a given field
# "searchBy" field should only ever be "name", "artist", "album", or "genre"
# Author: Joseph Britton (jtb8595)
#
@bp.route("/search", method=["GET", "POST"])
@login_required
def search_songs():
    if request.methon == "POST":
        search_term = request.form["search"].strip() # Whatever's in the search bar
        search_by = request.form["search_by"].strip() # Replace when above comment is implemented
    
        db_conn = get_db()
        try:
            with db_conn.cursor as curs:
                if search_by == "name":
                    curs.execute(
                        'SELECT s.name, ar.name, al.name, s.length, s.song_id ' \
                        'FROM "song" AS s ' \
                        'INNER JOIN "makesong" AS m ON s.song_id = m.song_id ' \
                        'INNER JOIN "artist" AS ar ON ar.artist_id = m.artist_id' \
                        'INNER JOIN "ispartofalbum" AS i ON s.song_id = i.song_id ' \
                        'INNER JOIN "album" AS al ON al.album_id = i.album_id '
                        'WHERE s.name = "%%%s%%"' \
                        'ORDER BY s.name ASC, ar.name ASC',
                        (search_term)
                    )

                elif search_by == "artist":
                    curs.execute(
                        'SELECT s.name, ar.name, al.name, s.length, s.song_id ' \
                        'FROM "song" AS s ' \
                        'INNER JOIN "makesong" AS m ON s.song_id = m.song_id ' \
                        'INNER JOIN "artist" AS ar ON ar.artist_id = m.artist_id' \
                        'INNER JOIN "ispartofalbum" AS al ON al.song_id = s.song_id' \
                        'WHERE ar.name = "%%%s%%"' \
                        'ORDER BY s.name ASC, ar.name ASC',
                        (search_term)
                    )
            
                elif search_by == "album":
                    curs.execute(
                        'SELECT s.name, ar.name, al.name, s.length, s.song_id ' \
                        'FROM "album" AS al'
                        'INNER JOIN "ispartofalbum" AS i ON i.album_id = al.album_id '
                        'INNER JOIN "song" AS s ON s.song_id = i.song_id '
                        'INNER JOIN "makesong" AS m ON s.song_id = m.song_id ' \
                        'INNER JOIN "artist" AS ar ON ar.artist_id = m.artist_id ' \
                        'WHERE al.name = "%%%s%%" '
                        'ORDER BY s.name ASC, ar.name ASC',
                        (search_term)
                    )

                elif search_by == "genre":
                    curs.execute(
                        'SELECT s.name, ar.name, al.name, s.length, s.song_id ' \
                        'FROM "genre" AS g'
                        'INNER JOIN "songhasgenre" AS h ON h.genre_id = g.genre_id '
                        'INNER JOIN "song" AS s ON s.song_id = h.song_id '
                        'INNER JOIN "makesong" AS m ON s.song_id = m.song_id ' \
                        'INNER JOIN "artist" AS ar ON ar.artist_id = m.artist_id ' \
                        'INNER JOIN "ispartofalbum" AS i ON s.song_id = i.song_id ' \
                        'INNER JOIN ""album" AS al ON i.album_id = al.album_id'
                        'WHERE g.name = "%%%s%%" '
                        'ORDER BY s.name ASC, ar.name ASC',
                        (search_term)
                    )
                
                # songs[x] = [song name, artist, album, song length, song_id]
                songs = curs.fetchall()
                song_ids, search_results = {}

                # Organize search results
                for song in songs:
                    # check if the song is not already in results
                    if song[5] not in song_ids:
                        # Not in results - add it
                        search_results.append([song[0], song[1], song[2], song[3]])
                        song_ids.append(song[5])
                    else:
                        # In results - add the artist
                        search_results[search_results.index(song[4])][1] += ", " + song[1]
            
                db_conn.commit()
        except psycopg.Error as e:
            db_conn.rollback()
            flash(f"Database error: {e}")
            return f"Database error: {e}", 500
    
    return render_template("search/results.html", results=search_results) # Replace with proper webpage render or w/e
