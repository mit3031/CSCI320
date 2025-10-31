INSERT INTO "user" (username, password, email, first_name, last_name, last_login, date_created) 
VALUES
    ('NovaSky', 'nova2525', 'nova.sky@gmail.com', 'Nova', 'Martinez', '2025-09-30 14:23:00', '2025-10-27 00:56:29'),
    ('AxelBlaze', 'blaze456', 'axel.blaze@gmail.com', 'Axel', 'Blake', '2025-09-29 18:45:00', '2022-12-11 11:15:00');

INSERT INTO song (song_id, title, release_date, length, is_explicit)
VALUES
    (1, 'Silver Horizons', '2022-03-15', 225, FALSE),
    (2, 'Neon Lights', '2023-06-21', 250, TRUE);

INSERT INTO artist (artist_id, name)
    VALUES
        (1, 'Night Drift'),
        (2, 'Aero Nova');

INSERT INTO collection (collection_id, name, creator_username)
    VALUES
        (1, 'Skyline Sessions', 'NovaSky'),
        (2, 'Blaze Beats', 'AxelBlaze');

INSERT INTO album (album_id, name, release_date)
    VALUES
        (1, 'Starlight Ritual', '2022-03-01'),
        (2, 'Mirage City', '2023-06-01');

INSERT INTO genre (genre_id, name)
    VALUES
        (1, 'Synthwave'),
        (2, 'Cyberpop');