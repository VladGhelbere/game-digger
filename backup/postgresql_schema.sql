-- DROP SCHEMA gd;

CREATE SCHEMA gd AUTHORIZATION root;

-- DROP SEQUENCE gd.customers_idx_seq;

CREATE SEQUENCE gd.customers_idx_seq
	INCREMENT BY 1
	MINVALUE 1
	MAXVALUE 2147483647
	START 1
	CACHE 1
	NO CYCLE;
-- DROP SEQUENCE gd.ratings_idx_seq;

CREATE SEQUENCE gd.ratings_idx_seq
	INCREMENT BY 1
	MINVALUE 1
	MAXVALUE 2147483647
	START 1
	CACHE 1
	NO CYCLE;
-- DROP SEQUENCE gd.requests_idx_seq;

CREATE SEQUENCE gd.requests_idx_seq
	INCREMENT BY 1
	MINVALUE 1
	MAXVALUE 2147483647
	START 1
	CACHE 1
	NO CYCLE;
-- DROP SEQUENCE gd.temp_games_idx_seq;

CREATE SEQUENCE gd.temp_games_idx_seq
	INCREMENT BY 1
	MINVALUE 1
	MAXVALUE 9223372036854775807
	START 1
	CACHE 1
	NO CYCLE;-- gd.games definition

-- Drop table

-- DROP TABLE gd.games;

CREATE TABLE gd.games (
	idx int8 NOT NULL GENERATED ALWAYS AS IDENTITY,
	id int8 NOT NULL,
	"name" text NOT NULL,
	slug text NOT NULL,
	platforms text NOT NULL,
	genres text NOT NULL,
	stores text NOT NULL,
	released text NOT NULL,
	rating float4 NOT NULL,
	CONSTRAINT id_unique_key_2 UNIQUE (id)
);


-- gd.ratings definition

-- Drop table

-- DROP TABLE gd.ratings;

CREATE TABLE gd.ratings (
	idx int4 NOT NULL GENERATED ALWAYS AS IDENTITY,
	user_idx int4 NOT NULL,
	game_id int8 NOT NULL,
	rating int4 NOT NULL,
	CONSTRAINT ratings_un UNIQUE (user_idx, game_id)
);


-- gd.requests definition

-- Drop table

-- DROP TABLE gd.requests;

CREATE TABLE gd.requests (
	idx int4 NOT NULL GENERATED ALWAYS AS IDENTITY,
	user_idx int4 NOT NULL,
	request text NOT NULL,
	request_time timestamp NOT NULL DEFAULT now()
);


-- gd.users definition

-- Drop table

-- DROP TABLE gd.users;

CREATE TABLE gd.users (
	idx int4 NOT NULL GENERATED ALWAYS AS IDENTITY,
	platform text NULL,
	username text NULL
);


-- gd.v_games source

CREATE OR REPLACE VIEW gd.v_games
AS SELECT games.id,
    games.slug,
    lower(games.platforms) AS platforms,
    lower(games.genres) AS genres,
    lower(games.stores) AS stores,
    "substring"(games.released, 0, 5) AS released,
    games.rating
   FROM gd.games;


-- gd.v_user_preferences source

CREATE OR REPLACE VIEW gd.v_user_preferences
AS SELECT u.username,
    r.rating,
    string_agg(vg.genres, ','::text) AS genres,
    string_agg(vg.released, ','::text) AS released
   FROM gd.ratings r
     JOIN gd.users u ON u.idx = r.user_idx
     JOIN gd.v_games vg ON r.game_id = vg.id
  WHERE r.rating > 2
  GROUP BY u.username, r.rating
  ORDER BY r.rating DESC, (count(vg.released)) DESC;

