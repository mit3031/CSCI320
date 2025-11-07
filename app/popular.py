#
# Implements popularity lists for songs and artists
# Author: Joseph Britton (jtb8595)
#

import psycopg

from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_login import login_required, login_user, logout_user, current_user
from .models import User
from .db import get_db
import datetime

bp = Blueprint("popular", __name__, url_prefix="/popular")

#
# Retrives the top 50 songs among the current user's followers
# As well as any data necessary to display them
# Author: Joseph Britton (jtb8595)
#
@bp.route("/followed", methods=["GET", "POST"])
@login_required
def followed_popular():
    if request.method == "POST":
        user = current_user.id

        db_conn = get_db()
        try:
            with db_conn.cursor() as curs:
                curs.execute(
                    'SELECT DISTINCT song.song_id, song.title, ar.name, al.name, g.name AS genre, ' \
                    'song.length, song.release_date, popular.times_listened ' \
                    'FROM ' \
                    '   (SELECT so.song_id, COUNT(l.datetime_listened) AS times_listened ' \
                    '   FROM "song" as so ' \
                    '   INNER JOIN ' \
                    '       (SELECT song_id, datetime_listened ' \
                    '       FROM "listentosong" AS lts ' \
                    '       WHERE lts.username IN ' \
                    '           (SELECT followed_username ' \
                    '           FROM "followuser" ' \
                    f'           WHERE follow_username = \'{user}\'))' \
                    '   AS l ON (so.song_id = l.song_id) ' \
                    '   GROUP BY so.song_id ' \
                    '   ORDER BY times_listened DESC ' \
                    '   LIMIT 50) ' \
                    'AS popular ' \
                    'INNER JOIN song ON (popular.song_id = song.song_id) ' \
                    'INNER JOIN makesong AS m ON (m.song_id = song.song_id) ' \
                    'INNER JOIN artist AS ar ON (ar.artist_id = m.artist_id) ' \
                    'INNER JOIN ispartofalbum AS i ON (i.song_id = song.song_id) ' \
                    'INNER JOIN album AS al ON (al.album_id = i.album_id) ' \
                    'INNER JOIN songhasgenre AS shg ON (shg.song_id = song.song_id) ' \
                    'INNER JOIN genre AS g ON (g.genre_id = shg.genre_id) ' \
                    'ORDER BY popular.times_listened DESC'
                )
                # popular[x] = [song id, song title, artist, album, genre, length, how many listens among followed users]
                popular = curs.fetchall()
                song_ids = [] # The ids of songs added to results (and which index they're at)

                # results[x] = {id: song id, name: title, artist: artist name...
                # ..., length: length, listen_count: how many times the FOLLOWED USERS have listened}
                results = [] 

                # Construct the results
                for entry in popular:
                        # check if the song is not already in results
                        if entry[0] not in song_ids:
                            # Not in results - add it
                            results.append({
                                "song_id": entry[0],
                                "name": entry[1], 
                                "artist": entry[2], 
                                "album": entry[3], 
                                "genre": entry[4],
                                "length": entry[5],
                                "release_date": entry[6],
                                "listen_count": entry[7]
                            })

                            # Add song id to running list of ids
                            song_ids.append(entry[0])
                        else:
                            toCheck = results[song_ids.index(entry[0])]
                            # In results - add the artist to song information if not already there
                            if entry[2] not in toCheck['artist']:
                                results[song_ids.index(entry[0])]['artist'] += ", " + entry[2]
                            # Do the same for album
                            if entry[3] not in toCheck['album']:
                                results[song_ids.index(entry[0])]['album'] += ", " + entry[3]
                            # Do the same for genre
                            if entry[4] and entry[4] not in toCheck['genre']:
                                results[song_ids.index(entry[0])]['genre'] += ", " + entry[4]

                # Warning for debug: <50 is possible, >50 should not be.
                if (len(results) > 50):
                    print(f"There's {len(results)} entries in results, " +
                        "which is supposed to be a top 50. Just a heads up." )
                
                db_conn.commit()
        except psycopg.Error as e:
            db_conn.rollback()
            flash(f"Database error: {e}")
            return f"Database error: {e}", 500
        
        
        return render_template("popular/results.html", results=results)
    
    return render_template("popular/popular.html")