-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

-- Drop all tables before recreating
DROP TABLE IF EXISTS matches;
DROP TABLE IF EXISTS players;

CREATE TABLE  players (
    player_id SERIAL NOT NULL,
    name TEXT NOT NULL,
    PRIMARY KEY (player_id)
);

CREATE TABLE matches (
    match_id SERIAL NOT NULL,
    winner_id INT NOT NULL REFERENCES players (player_id),
    loser_id INT NOT NULL REFERENCES players (player_id),
    PRIMARY KEY (match_id)
);
