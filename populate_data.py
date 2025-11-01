

import os
from dotenv import load_dotenv
import random
from datetime import datetime
from faker import Faker
import psycopg
from sshtunnel import SSHTunnelForwarder
import atexit

load_dotenv()
RIT_USERNAME=os.getenv("RIT_USERNAME")
RIT_PASSWORD=os.getenv("RIT_PASSWORD")
DB_NAME=os.getenv("DB_NAME")

fake = Faker()
server = None

def start_ssh():
    global server
    if server is None or not server.is_active:        
        server = SSHTunnelForwarder(
            ('starbug.cs.rit.edu', 22),
            ssh_username=RIT_USERNAME,
            ssh_password=RIT_PASSWORD,
            remote_bind_address=('127.0.0.1', 5432)
        )
        server.start()
        atexit.register(server.stop)

def get_con():
    if server is None or not server.is_active:
        raise RuntimeError("SSH tunnel not active")
    try:
        return psycopg.connect(
            dbname=DB_NAME,
            user=RIT_USERNAME,
            password=RIT_PASSWORD,
            host='localhost',
            port=server.local_bind_port
        )
    except psycopg.Error as e:
        print(f"Failed to connect to the database {e}")
        raise e

def rand_date(start_year=2020, end_year=2025):
    start = datetime(start_year, 1, 1)
    end = datetime(end_year, 12, 31)
    return fake.date_between_dates(start, end)

def rand_timestamp(start_year=2020, end_year=2025):
    start = datetime(start_year, 1, 1)
    end = datetime(end_year, 12, 31)
    return fake.date_time_between_dates(start, end)

def populate_users(con, n=6000):
    cur = con.cursor()
    cur.execute('SELECT username FROM "user"')
    users = set(row[0] for row in cur.fetchall())
    cur.execute('SELECT email FROM "user"')
    emails = set(row[0] for row in cur.fetchall())
    for _ in range(n):
        while True:
            base_username = fake.user_name().replace('.', '').replace('_', '').replace('-', '')
            base_username = base_username[:15]
            username = base_username + str(random.randint(0, 9999))
            if username not in users:
                users.add(username)
                break
        while True:
            email = fake.email()
            if email not in emails:
                emails.add(email)
                break
        password = fake.password(length=20)
        first_name = fake.first_name()
        while len(first_name) > 20:
            first_name = fake.first_name()
        last_name = fake.last_name()
        while len(last_name) > 20:
            last_name = fake.last_name()
        date_created = rand_timestamp(2019, 2025)
        last_login = fake.date_time_between_dates(datetime_start=date_created, datetime_end=datetime(2025, 12, 31))
        cur.execute("""
            INSERT INTO "user"(username, password, email, first_name, last_name, last_login, date_created)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (username, password, email, first_name, last_name, last_login, date_created))
    con.commit()

def populate_artists(con, n=3000):
    cur = con.cursor()
    cur.execute("SELECT name FROM artist")
    artists = set(row[0] for row in cur.fetchall())
    for _ in range(n):
        while True:
            name = fake.name()
            if name not in artists:
                artists.add(name)
                break
        cur.execute("INSERT INTO artist(name) VALUES (%s)", (name,))
    con.commit()

def populate_genres(con, n=20):
    cur = con.cursor()
    cur.execute("SELECT name FROM genre")
    existing_genres = set(row[0] for row in cur.fetchall())
    base_genres = ['Rock', 'Pop', 'Jazz', 'Hip Hop', 'Electronic', 'Country', 'R&B', 'Classical', 
                'Metal', 'Indie', 'Folk', 'Blues', 'Reggae', 'Latin', 'Punk', 'Soul', 'Alternative', 
                'Gospel', 'Funk', 'House', 'Techno', 'Disco', 'Ambient', 'Wave', 'Step', 'Bass', 'Tech']
    modifiers = ['Synth', 'Cyber', 'Electro', 'Chill', 'Dream', 'Future', 'Neo', 'Dark', 'Acid', 
                'Trap', 'Vapor', 'Retro', 'Space', 'Crystal', 'Liquid', 'Glitch']
    
    pool = []

    for base in base_genres:
        pool.append(base)
    for modifier in modifiers:
        for base in base_genres:
            genre_name = modifier + base
            if len(genre_name) <= 20:
                pool.append(genre_name)

    avail_genres = [g for g in pool if g.lower() not in existing_genres]

    i = min(n, len(avail_genres))
    genres_added = random.sample(avail_genres, i)

    for genre_name in genres_added:
        cur.execute("INSERT INTO genre(name) VALUES (%s)", (genre_name,))

    con.commit()

def populate_songs(con, n=7000):
    cur = con.cursor()
    title_words = ['Love', 'Heart', 'Night', 'Dream', 'Fire', 'Rain', 'Blue', 'Summer', 'Winter', 
                'Dance', 'Soul', 'Light', 'Dark', 'Moon', 'Star', 'Sun', 'Wild', 'Sweet', 
                'Paradise', 'Heaven', 'Angel', 'Devil', 'Thunder', 'Lightning', 'Storm', 
                'Ocean', 'River', 'Mountain', 'Sky', 'Midnight', 'Morning', 'Yesterday', 
                'Tomorrow', 'Forever', 'Never', 'Always', 'Magic', 'Mystery', 'Freedom']
    
    titles = set()
    while len(titles) < n:
        if random.random() < 0.5:
            title = random.choice(title_words) + ' ' + random.choice(title_words)
        else:
            title = random.choice(title_words) + ' ' + random.choice(['in', 'on', 'of', 'for']) + ' ' + random.choice(title_words)
        titles.add(title)
    
    data = []
    for title in titles:
        release_date = rand_date()
        length = random.randint(60, 600)
        is_explicit = random.choice([True, False])
        data.append((title, release_date, length, is_explicit))
    
    cur.executemany("""
        INSERT INTO song(title, release_date, length, is_explicit)
        VALUES (%s, %s, %s, %s)
    """, data)
    con.commit()

def populate_albums(con, n=2000):
    cur = con.cursor()
    cur.execute("SELECT name FROM album")
    albums = set(row[0] for row in cur.fetchall())
    inserted = 0
    while inserted < n:
        name = fake.sentence(nb_words=2).replace('.', '')
        if name not in albums:
            albums.add(name)
            release_date = rand_date()
            cur.execute("INSERT INTO album(name, release_date) VALUES (%s, %s)", (name, release_date))
            inserted += 1
    con.commit()

def populate_collections(con, n=2000):
    cur = con.cursor()
    cur.execute("SELECT username FROM \"user\"")
    users = [row[0] for row in cur.fetchall()]
    for _ in range(n):
        name = fake.sentence(nb_words=2)
        creator = random.choice(users)
        cur.execute("INSERT INTO collection(name, creator_username) VALUES (%s, %s)", (name, creator))
    con.commit()

def populate_albums(con, n=2000):
    cur = con.cursor()
    cur.execute("SELECT name FROM album")
    existing = set(row[0] for row in cur.fetchall())
    
    albums = set()
    while len(albums) < n:
        name = fake.sentence(nb_words=2).replace('.', '')
        if name not in existing:
            albums.add(name)
    
    data = [(name, rand_date()) for name in albums]
    cur.executemany("INSERT INTO album(name, release_date) VALUES (%s, %s)", data)
    con.commit()

def populate_collections(con, n=2000):
    cur = con.cursor()
    cur.execute("SELECT username FROM \"user\"")
    users = [row[0] for row in cur.fetchall()]
    
    data = [(fake.sentence(nb_words=2), random.choice(users)) for _ in range(n)]
    cur.executemany("INSERT INTO collection(name, creator_username) VALUES (%s, %s)", data)
    con.commit()

def populate_follow_users(con, n=5000):
    cur = con.cursor()
    cur.execute("SELECT username FROM \"user\"")
    users = [row[0] for row in cur.fetchall()]
    
    data = []
    for follower in users:
        follows = random.sample([user for user in users if user != follower], k=random.randint(1, 5))
        for followed in follows:
            if len(data) >= n:
                break
            data.append((follower, followed))
        if len(data) >= n:
            break

    cur.executemany("INSERT INTO followuser(follow_username, followed_username) VALUES (%s, %s)", data)
    con.commit()

def populate_make_song(con):
    cur = con.cursor()
    cur.execute("SELECT artist_id FROM artist")
    artists = [row[0] for row in cur.fetchall()]
    cur.execute("SELECT song_id FROM song")
    songs = [row[0] for row in cur.fetchall()]
    cur.execute("SELECT artist_id, song_id FROM makesong")
    artist_song = set(cur.fetchall())
    
    data = []
    song_to_artists = {song_id: set() for song_id in songs}
    artist_to_songs = {artist_id: set() for artist_id in artists}

    for artist_id, song_id in artist_song:
        song_to_artists[song_id].add(artist_id)
        artist_to_songs[artist_id].add(song_id)

    for artist_id in artists:
        if not artist_to_songs[artist_id]:
            song_id = random.choice(songs)
            data.append((artist_id, song_id))
            song_to_artists[song_id].add(artist_id)
            artist_to_songs[artist_id].add(song_id)
    
    for song_id in songs:
        has_song = song_to_artists[song_id] #artists that have a song
        need = random.randint(1, 2)
        if len(has_song) < need:
            avail_artists = [artist for artist in artists if artist not in has_song]
            count = min(need - len(has_song), len(avail_artists))
            new_artists = random.sample(avail_artists, k=count)
            for artist_id in new_artists:
                data.append((artist_id, song_id))
                song_to_artists[song_id].add(artist_id)
                artist_to_songs[artist_id].add(song_id)
    
    cur.executemany("INSERT INTO makesong(artist_id, song_id) VALUES (%s, %s) ON CONFLICT DO NOTHING", data)
    con.commit()

def populate_make_album(con):
    cur = con.cursor()
    cur.execute("SELECT artist_id FROM artist")
    artists = [row[0] for row in cur.fetchall()]
    cur.execute("SELECT album_id FROM album")
    albums = [row[0] for row in cur.fetchall()]
    
    cur.execute("SELECT artist_id, album_id FROM makealbum")
    artist_album = set(cur.fetchall())
    
    artist_to_albums = {artist_id: set() for artist_id in artists}
    album_to_artists = {album_id: set() for album_id in albums}
    for artist_id, album_id in artist_album:
        artist_to_albums[artist_id].add(album_id)
        album_to_artists[album_id].add(artist_id)
    data = []

    for artist_id in artists:
        if not artist_to_albums[artist_id]:
            album_id = random.choice(albums)
            data.append((artist_id, album_id))
            artist_to_albums[artist_id].add(album_id)
            album_to_artists[album_id].add(artist_id)
    
    for album_id in albums:
        if not album_to_artists[album_id]:
            artist_id = random.choice(artists)
            data.append((artist_id, album_id))
            artist_to_albums[artist_id].add(album_id)
            album_to_artists[album_id].add(artist_id)
    
    for album_id in albums:
        avail_artists = [artist for artist in artists if artist not in album_to_artists[album_id]]
        if avail_artists:
            new_artists = random.sample(avail_artists, k=min(len(avail_artists), random.randint(1, 2)))
            for artist_id in new_artists:
                if(artist_id, album_id) not in artist_album and (artist_id, album_id) not in data:
                    data.append((artist_id, album_id))
                    artist_to_albums[artist_id].add(album_id)
                    album_to_artists[album_id].add(artist_id)
    
    cur.executemany("INSERT INTO makealbum(artist_id, album_id) VALUES (%s, %s) ON CONFLICT DO NOTHING", data)
    con.commit()

def populate_is_part_of_album(con):
    cur = con.cursor()
    cur.execute("SELECT song_id FROM song")
    songs = [row[0] for row in cur.fetchall()]
    cur.execute("SELECT album_id FROM album")
    albums = [row[0] for row in cur.fetchall()]
    
    song_to_albums = {song_id: set() for song_id in songs}
    album_to_songs = {album_id: set() for album_id in albums}
    data = []

    for song_id in songs:
        need = random.randint(1, 2)
        avail_albums = [album for album in albums if album not in song_to_albums[song_id]]
        count = min(need, len(avail_albums))
        selected_albums = random.sample(avail_albums, count)
        for album_id in selected_albums:
            track_num = len(album_to_songs[album_id]) + 1
            data.append((song_id, album_id, track_num))
            song_to_albums[song_id].add(album_id)
            album_to_songs[album_id].add(song_id)
    
    for album_id in albums:
        if not album_to_songs[album_id]:
            song_id = random.choice(songs)
            data.append((song_id, album_id, 1))
            song_to_albums[song_id].add(album_id)
            album_to_songs[album_id].add(song_id)
    
    cur.executemany("INSERT INTO ispartofalbum(song_id, album_id, track_num) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING", data)
    con.commit()

def populate_song_has_genre(con):
    cur = con.cursor()
    cur.execute("SELECT song_id FROM song")
    songs = [row[0] for row in cur.fetchall()]
    cur.execute("SELECT genre_id FROM genre")
    genres = [row[0] for row in cur.fetchall()]

    song_to_genres = {song_id: set() for song_id in songs}
    genre_to_songs = {genre_id: set() for genre_id in genres}
    data = []

    for song_id in songs:
        need = random.randint(1, 3)
        avail_genres = [genre for genre in genres if genre not in song_to_genres[song_id]]
        count = min(need, len(avail_genres))
        selected_genres = random.sample(avail_genres, count)
        for genre_id in selected_genres:
            data.append((song_id, genre_id))
            song_to_genres[song_id].add(genre_id)
            genre_to_songs[genre_id].add(song_id)
    
    cur.executemany("INSERT INTO songhasgenre(song_id, genre_id) VALUES (%s, %s) ON CONFLICT DO NOTHING", data)
    con.commit()

def populate_album_has_genre(con):
    cur = con.cursor()
    cur.execute("SELECT album_id FROM album")
    albums = [row[0] for row in cur.fetchall()]
    cur.execute("SELECT genre_id FROM genre")
    genres = [row[0] for row in cur.fetchall()]
    
    album_to_genres = {album_id: set() for album_id in albums}
    genre_to_albums = {genre_id: set() for genre_id in genres}
    data = []

    for album_id in albums:
        need = random.randint(1, 2)
        avail_genres = [genre for genre in genres if genre not in album_to_genres[album_id]]
        count = min(need, len(avail_genres))
        selected_genres = random.sample(avail_genres, count)
        for genre_id in selected_genres:
            data.append((album_id, genre_id))
            album_to_genres[album_id].add(genre_id)
            genre_to_albums[genre_id].add(album_id)
    
    cur.executemany("INSERT INTO albumhasgenre(album_id, genre_id) VALUES (%s, %s)  ON CONFLICT DO NOTHING" , data)
    con.commit()

def sync_music(con):
    cur = con.cursor()

    cur.execute("SELECT song_id, album_id FROM ispartofalbum")
    album_songs = {}
    for song_id, album_id in cur.fetchall():
        album_songs.setdefault(album_id, set()).add(song_id)

    cur.execute("SELECT artist_id, song_id FROM makesong")
    song_artists = {}
    for artist_id, song_id in cur.fetchall():
        song_artists.setdefault(song_id, set()).add(artist_id)

    cur.execute("SELECT song_id, genre_id FROM songhasgenre")
    song_genres = {}
    for song_id, genre_id in cur.fetchall():
        song_genres.setdefault(song_id, set()).add(genre_id)

    cur.execute("SELECT artist_id, album_id FROM makealbum")
    album_artists = {}
    for artist_id, album_id in cur.fetchall():
        album_artists.setdefault(album_id, set()).add(artist_id)

    cur.execute("SELECT album_id, genre_id FROM albumhasgenre")
    album_genres = {}
    for album_id, genre_id in cur.fetchall():
        album_genres.setdefault(album_id, set()).add(genre_id)

    new_makealbum = []
    new_albumgenre = []

    for album_id, song_ids in album_songs.items():
        needed_artists = set()
        needed_genres = set()
        for song_id in song_ids:
            needed_artists.update(song_artists.get(song_id, set()))
            needed_genres.update(song_genres.get(song_id, set()))

        current_artists = album_artists.get(album_id, set())
        current_genres = album_genres.get(album_id, set())

        missing_artists = needed_artists - current_artists
        missing_genres = needed_genres - current_genres

        for artist_id in missing_artists:
            new_makealbum.append((artist_id, album_id))
        for genre_id in missing_genres:
            new_albumgenre.append((album_id, genre_id))

    if new_makealbum:
        cur.executemany(
            "INSERT INTO makealbum(artist_id, album_id) VALUES (%s, %s) ON CONFLICT DO NOTHING",
            new_makealbum,
        )

    if new_albumgenre:
        cur.executemany(
            "INSERT INTO albumhasgenre(album_id, genre_id) VALUES (%s, %s) ON CONFLICT DO NOTHING",
            new_albumgenre,
        )

    con.commit()

def populate_is_part_of_collection(con, n=5000):
    cur = con.cursor()
    cur.execute("SELECT collection_id FROM collection")
    collections = [row[0] for row in cur.fetchall()]
    cur.execute("SELECT song_id FROM song")
    songs = [row[0] for row in cur.fetchall()]
    
    data = []
    for collection_id in collections:
        selected_songs = random.sample(songs, k=random.randint(5,20))
        for song_id in selected_songs:
            if len(data) >= n:
                break
            data.append((collection_id, song_id))
        if len(data) >= n:
            break
    
    cur.executemany("INSERT INTO ispartofcollection(collection_id, song_id) VALUES (%s, %s)", data)
    con.commit()

def populate_listen_to_song(con, n=5000):
    cur = con.cursor()
    cur.execute("SELECT username FROM \"user\"")
    users = [row[0] for row in cur.fetchall()]
    cur.execute("SELECT song_id FROM song")
    songs = [row[0] for row in cur.fetchall()]
    
    data = []
    for username in users:
        listened_songs = random.sample(songs, k=random.randint(5,15))
        for song_id in listened_songs:
            if len(data) >= n:
                break
            data.append((username, song_id, rand_timestamp()))
        if len(data) >= n:
            break
    
    cur.executemany("INSERT INTO listentosong(username, song_id, datetime_listened) VALUES (%s, %s, %s)", data)
    con.commit()

def populate_song_rating(con, n=5000):
    cur = con.cursor()
    cur.execute("SELECT username FROM \"user\"")
    users = [row[0] for row in cur.fetchall()]
    cur.execute("SELECT song_id FROM song")
    songs = [row[0] for row in cur.fetchall()]
    
    data = []
    for username in users:
        rated_songs = random.sample(songs, k=random.randint(3,10))
        for song_id in rated_songs:
            if len(data) >= n:
                break
            rating = random.randint(1, 5)
            liked = rating >= 3
            data.append((username, song_id, liked, rating))
        if len(data) >= n:
            break
    
    cur.executemany("INSERT INTO songrating(username, song_id, liked, rating) VALUES (%s, %s, %s, %s)", data)
    con.commit()

def main():
    try:
        start_ssh()
        con = get_con()
        
        populate_users(con)
        populate_artists(con)
        populate_genres(con)
        populate_songs(con)
        populate_albums(con)
        populate_collections(con)
        populate_follow_users(con)
        populate_make_song(con)
        populate_make_album(con)
        populate_is_part_of_album(con)
        populate_song_has_genre(con)
        populate_album_has_genre(con)
        sync_music(con)
        populate_is_part_of_collection(con)
        populate_listen_to_song(con)
        populate_song_rating(con)
        
        con.close()
    except Exception as e:
        print(f"Error: {e}")
        raise

if __name__ == "__main__":
    main()

