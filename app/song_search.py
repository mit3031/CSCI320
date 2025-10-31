#
# Implements the search queries for songs
# Author: Joseph Britton (jtb8595)
#

import psycopg

from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_login import login_required, login_user, logout_user, current_user
from .models import User
from .db import get_db

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
        search_term = request.form["search"].strip() # Whatever's in the search bar
        search_by = request.form["search_by"].strip() # Should be a dropdown
        user = current_user.id
    
        db_conn = get_db()
        try:
            with db_conn.cursor() as curs:
                if search_by == "name":
                    print(f"Searching for {search_term} in name")
                    curs.execute(
                        'SELECT so.song_id, so.title, ar.name, al.name, so.length ' \
                        'FROM "song" AS so ' \
                        'INNER JOIN "makesong" AS m ON (so.song_id = m.song_id) ' \
                        'INNER JOIN "artist" AS ar ON (ar.artist_id = m.artist_id) ' \
                        'INNER JOIN "ispartofalbum" AS i ON (so.song_id = i.song_id) ' \
                        'INNER JOIN "album" AS al ON (al.album_id = i.album_id) ' \
                        f'WHERE (so.title LIKE \'%%{search_term}%%\') ' \
                        'ORDER BY so.title ASC, ar.name ASC',
                        []
                    )

                elif search_by == "artist":
                    print(f"Searching for {search_term} in artist")
                    curs.execute(
                        'SELECT so.song_id, so.title, ar.name, al.name,  so.length ' \
                        'FROM "song" AS so ' \
                        'INNER JOIN "makesong" AS m ON (so.song_id = m.song_id) ' \
                        'INNER JOIN "artist" AS ar ON (ar.artist_id = m.artist_id) ' \
                        'INNER JOIN "ispartofalbum" AS i ON (so.song_id = i.song_id) '
                        'INNER JOIN "album" AS al ON (al.album_id = i.album_id) ' \
                        f'WHERE ar.name LIKE \'%%{search_term}%%\' ' \
                        'ORDER BY so.title ASC, ar.name ASC',
                        []
                    )
            
                elif search_by == "album":
                    print(f"Searching for {search_term} in album")
                    curs.execute(
                        'SELECT  so.song_id,  so.title, ar.name, al.name,  so.length ' \
                        'FROM "album" AS al ' \
                        'INNER JOIN "ispartofalbum" AS i ON (i.album_id = al.album_id) ' \
                        'INNER JOIN "song" AS so ON (so.song_id = i.song_id) ' \
                        'INNER JOIN "makesong" AS m ON (so.song_id = m.song_id) ' \
                        'INNER JOIN "artist" AS ar ON (ar.artist_id = m.artist_id) ' \
                        f'WHERE al.name LIKE \'%%{search_term}%%\' ' \
                        'ORDER BY so.title ASC, ar.name ASC',
                        []
                    )

                elif search_by == "genre":
                    print(f"Searching for {search_term} in genre")
                    curs.execute(
                        'SELECT  so.song_id,  so.title, ar.name, al.name,  so.length ' \
                        'FROM "genre" AS g ' \
                        'INNER JOIN "songhasgenre" AS h ON (h.genre_id = g.genre_id) ' \
                        'INNER JOIN "song" AS so ON (so.song_id = h.song_id) ' \
                        'INNER JOIN "makesong" AS m ON (so.song_id = m.song_id) ' \
                        'INNER JOIN "artist" AS ar ON (ar.artist_id = m.artist_id) ' \
                        'INNER JOIN "ispartofalbum" AS i ON (so.song_id = i.song_id) ' \
                        'INNER JOIN "album" AS al ON (i.album_id = al.album_id) ' \
                        f'WHERE g.name LIKE \'%%{search_term}%%\' ' \
                        'ORDER BY so.title ASC, ar.name ASC',
                        []
                    )
                
                # songs[x] = [song id, song name, artist, album, song length]
                songs = curs.fetchall()
                song_ids = []
                results = [] # [name, artist, album, length, number of times listened]

                # Organize search results
                for song in songs:
                    # check if the song is not already in results
                    if song[0] not in song_ids:
                        # Not in results - add it

                        # Get times listened to song
                        curs.execute(
                            'SELECT COUNT(*)' \
                            'FROM "listentosong" ' \
                            f'WHERE username = \'{user}\' AND song_id = {song[0]}',
                            []
                        )

                        # Add song information to results
                        results.append({
                            "name": song[1], 
                            "artist": song[2], 
                            "album": song[3], 
                            "length": song[4], 
                            "listened": curs.fetchone()[0]})
                        song_ids.append(song[0])
                    else:
                        toCheck = results[song_ids.index(song[0])]
                        # In results - add the artist to song information if not already there
                        if song[2] not in toCheck['artist']:
                            results[song_ids.index(song[0])]['artist'] += ", " + song[2]
                        # Do the same for album
                        if song[3] not in toCheck['album']:
                            results[song_ids.index(song[0])]['album'] += ", " + song[3]
            
                db_conn.commit()
        except psycopg.Error as e:
            db_conn.rollback()
            flash(f"Database error: {e}")
            return f"Database error: {e}", 500
    
        return render_template("search/results.html", results=results)

    return render_template("search/search.html")
