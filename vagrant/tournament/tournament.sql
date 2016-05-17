-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

CREATE TABLE players ( name TEXT,
					id SERIAL as primary key);
					 
CREATE TABLE matches ( left_id integer references players(id),
					right_id integer references players(id),
					winner integer default 0,
					primary key (left_id, right_id),
					CHECK (winner = left_id or winner = right_id or winner = 0),
					CHECK (left_id < right_id));
