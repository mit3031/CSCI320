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
    return fake.date_between_dates(start_date=start, end_date = end)

def rand_timestamp(start_year=2020, end_year=2025):
    start = datetime(start_year, 1, 1)
    end = datetime(end_year, 12, 31)
    return fake.date_time_between_dates(datetime_start=start, datetime_end=end)

def populate_users(con, n=6000):
    cur = con.cursor()
    users = set()
    for _ in range(n):
        while True:
            base_username = fake.user_name().replace('.', '').replace('_', '').replace('-', '')
            username = base_username + str(random.randint(0, 9999))
            if username not in users:
                users.add(username)
                break
        password = fake.password(length=20)
        email = fake.email()
        first_name = fake.first_name()
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
    artists = set()
    for _ in range(n):
        while True:
            name = fake.name()
            if name not in artists:
                artists.add(name)
                break
        cur.execute("INSERT INTO artist(name) VALUES (%s)", (name,))
    con.commit()

def populate_genres(con, n=30):
    cur = con.cursor()
    cur.execute("SELECT name FROM genre")
    existing_genres = set(row[0].lower() for row in cur.fetchall())
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
            pool.append(modifier + base)

    avail_genres = [g for g in pool if g.lower() not in existing_genres]

    i = min(n, len(avail_genres))
    genres_added = random.sample(avail_genres, i)

    for genre_name in genres_added:
        cur.execute("INSERT INTO genre(name) VALUES (%s)", (genre_name,))

    con.commit()

def populate_songs(con, n=10000):
    cur = con.cursor()
    title_words = ['Love', 'Heart', 'Night', 'Dream', 'Fire', 'Rain', 'Blue', 'Summer', 'Winter', 
                'Dance', 'Soul', 'Light', 'Dark', 'Moon', 'Star', 'Sun', 'Wild', 'Sweet', 
                'Paradise', 'Heaven', 'Angel', 'Devil', 'Thunder', 'Lightning', 'Storm', 
                'Ocean', 'River', 'Mountain', 'Sky', 'Midnight', 'Morning', 'Yesterday', 
                'Tomorrow', 'Forever', 'Never', 'Always', 'Magic', 'Mystery', 'Freedom']
    titles = set()
    inserted = 0
    while inserted < n:
        if random.random() < 0.5:
            title = random.choice(title_words) + ' ' + random.choice(title_words)
        else:
            title = random.choice(title_words) + ' ' + random.choice(['in', 'on', 'of', 'for']) + ' ' + random.choice(title_words)
        
        if title not in titles:
            titles.add(title)
            release_date = rand_date()
            length = random.randint(60, 600)
            is_explicit = random.choice([True, False])
            cur.execute("""
                INSERT INTO song(title, release_date, length, is_explicit)
                VALUES (%s, %s, %s, %s)
            """, (title, release_date, length, is_explicit))
            inserted += 1
    con.commit()

def populate_albums(con, n=2000):
    cur = con.cursor()
    albums = set()
    inserted = 0
    while inserted < n:
        name = fake.sentence(nb_words=2)
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

def populate_follow_users(con):
    cur = con.cursor()
    cur.execute("SELECT username FROM \"user\"")
    users = [row[0] for row in cur.fetchall()]
    for follower in users:
        follows = random.sample([user for user in users if user != follower], k=random.randint(1, 5))
        for followed in follows:
            cur.execute("INSERT INTO followuser(follower_username, followed_username) VALUES (%s, %s)", (follower, followed))
    con.commit()

def populate_make_song(con):
    cur = con.cursor()
    cur.execute("SELECT id FROM artist")
    artists = [row[0] for row in cur.fetchall()]
    cur.execute("SELECT id FROM song")
    songs = [row[0] for row in cur.fetchall()]
    for song_id in songs:
        selected_artists = random.sample(artists, k=random.randint(1,3))
        for artist_id in selected_artists:
            cur.execute("INSERT INTO makesong(artist_id, song_id) VALUES (%s, %s)", (artist_id, song_id))
    con.commit()

def populate_make_album(con):
    cur = con.cursor()
    cur.execute("SELECT id FROM artist")
    artists = [row[0] for row in cur.fetchall()]
    cur.execute("SELECT id FROM album")
    albums = [row[0] for row in cur.fetchall()]
    for album_id in albums:
        selected_artists = random.sample(artists, k=random.randint(1,2))
        for artist_id in selected_artists:
            cur.execute("INSERT INTO makealbum(artist_id, album_id) VALUES (%s, %s)", (artist_id, album_id))
    con.commit()

def populate_is_part_of_album(con):
    cur = con.cursor()
    cur.execute("SELECT id FROM song")
    songs = [row[0] for row in cur.fetchall()]
    cur.execute("SELECT id FROM album")
    albums = [row[0] for row in cur.fetchall()]
    for album_id in albums:
        album_songs = random.sample(songs, k=random.randint(3,8))
        for track_num, song_id in enumerate(album_songs, start=1):
            cur.execute("INSERT INTO ispartofalbum(song_id, album_id, track_num) VALUES (%s, %s, %s)", (song_id, album_id, track_num))
    con.commit()

def populate_song_has_genre(con):
    cur = con.cursor()
    cur.execute("SELECT id FROM song")
    songs = [row[0] for row in cur.fetchall()]
    cur.execute("SELECT id FROM genre")
    genres = [row[0] for row in cur.fetchall()]
    for song_id in songs:
        selected_genres = random.sample(genres, k=random.randint(1,3))
        for genre_id in selected_genres:
            cur.execute("INSERT INTO songhasgenre(song_id, genre_id) VALUES (%s, %s)", (song_id, genre_id))
    con.commit()

def populate_album_has_genre(con):
    cur = con.cursor()
    cur.execute("SELECT id FROM album")
    albums = [row[0] for row in cur.fetchall()]
    cur.execute("SELECT id FROM genre")
    genres = [row[0] for row in cur.fetchall()]
    for album_id in albums:
        selected_genres = random.sample(genres, k=random.randint(1,2))
        for genre_id in selected_genres:
            cur.execute("INSERT INTO albumhasgenre(album_id, genre_id) VALUES (%s, %s)", (album_id, genre_id))
    con.commit()

def populate_is_part_of_collection(con):
    cur = con.cursor()
    cur.execute("SELECT id FROM collection")
    collections = [row[0] for row in cur.fetchall()]
    cur.execute("SELECT id FROM song")
    songs = [row[0] for row in cur.fetchall()]
    for collection_id in collections:
        selected_songs = random.sample(songs, k=random.randint(5,20))
        for song_id in selected_songs:
            cur.execute("INSERT INTO ispartofcollection(collection_id, song_id) VALUES (%s, %s)", (collection_id, song_id))
    con.commit()

def populate_listen_to_song(con):
    cur = con.cursor()
    cur.execute("SELECT username FROM \"user\"")
    users = [row[0] for row in cur.fetchall()]
    cur.execute("SELECT id FROM song")
    songs = [row[0] for row in cur.fetchall()]
    for username in users:
        listened_songs = random.sample(songs, k=random.randint(5,15))
        for song_id in listened_songs:
            listened_at = rand_timestamp()
            cur.execute("INSERT INTO listentosong(username, song_id, datetime_listened) VALUES (%s, %s, %s)", (username, song_id, listened_at))
    con.commit()

def populate_song_rating(con):
    cur = con.cursor()
    cur.execute("SELECT username FROM \"user\"")
    users = [row[0] for row in cur.fetchall()]
    cur.execute("SELECT id FROM song")
    songs = [row[0] for row in cur.fetchall()]
    for username in users:
        rated_songs = random.sample(songs, k=random.randint(3,10))
        for song_id in rated_songs:
            rating = random.randint(1, 5)
            cur.execute("INSERT INTO songrating(username, song_id, rating) VALUES (%s, %s, %s)", (username, song_id, rating))
    con.commit()

# --- Main Execution ---
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
        populate_is_part_of_collection(con)
        populate_listen_to_song(con)
        populate_song_rating(con)
        
        con.close()
        
    except Exception as e:
        print(f"Error: {e}")
        raise

if __name__ == "__main__":
    main()

