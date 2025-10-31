CREATE TABLE "user" (
    username VARCHAR(20) PRIMARY KEY,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(100) NOT NULL,
    first_name VARCHAR(20) NOT NULL,
    last_name VARCHAR(20) NOT NULL,
    last_login TIMESTAMP,
    date_created TIMESTAMP default now()
);

CREATE TABLE song (
    song_id BIGINT PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    release_date date,
    length SMALLINT,
    is_explicit boolean
);