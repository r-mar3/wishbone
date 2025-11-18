IF EXISTS DROP DATABASE wishbone;
CREATE DATABASE wishbone;

\c wishbone;

CREATE TABLE game (
    game_id INT GENERATED ALWAYS AS IDENTITY,
    game_name TEXT NOT NULL,
    retail_price INT NOT NULL,
    PRIMARY KEY(game_id)
);

CREATE TABLE tracking (
    tracking_id INT GENERATED ALWAYS AS IDENTITY,
    email TEXT NOT NULL,
    game_id NOT NULL,
    PRIMARY KEY(tracking_id),
    FOREIGN KEY (game_id) REFERENCES game(game_id)
);

CREATE TABLE platform(
    platform_id INT GENERATED ALWAYS AS IDENTITY,
    platform_name TEXT NOT NULL,
    PRIMARY KEY(platform_id)
);

CREATE TABLE listing(
    listing_id INT GENERATED ALWAYS AS IDENTITY,
    platform_code TEXT NOT NULL,
    game_id INT NOT NULL,
    platform_id INT NOT NULL,
    PRIMARY KEY(listing_id),
    FOREIGN KEY (game_id) REFERENCES game(game_id)
    FOREIGN KEY (platform_id) REFERENCES platform(platform_id)
);

CREATE TABLE price_record(
    price_record_id INT GENERATED ALWAYS AS IDENTITY,
    listing_id INT NOT NULL,
    price INT NOT NULL,
    discount_percent INT,
    recording_date DATE CHECK recording_date <= CURRENT_DATE,
    PRIMARY KEY(price_record_id)
    FOREIGN KEY (listing_id) REFERENCES listing(listing_id)
);