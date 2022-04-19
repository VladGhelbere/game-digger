import os, logging
import lib.rawg_wrapper as rawg_wrapper
import lib.postgres_wrapper as postgres_wrapper
from game import *

BOT_SYMBOL = os.getenv("BOT_SYMBOL")

class GameRecommender():
    def __init__(self):
        logging.basicConfig(filename=f"{os.getenv('LOG_PATH')}recommender.log",
            format="%(asctime)s - %(levelname)s - %(message)s",
            datefmt="%d-%b-%y %H:%M:%S")
        try:
            self.RAWG_API = rawg_wrapper.rawg_wrapper()
            self.PG_WRAPPER = postgres_wrapper.DB()
        except Exception as e:
            exit(-1)

    # Uses: DB
    # Responds to: game
    def fetch_random_game(self, requester):
        try:
            game_info = self.PG_WRAPPER.get_rows("SELECT name, slug, platforms, genres, stores, released, rating  FROM gd.games  ORDER BY RANDOM() LIMIT 1")[0]
            game_obj = Game(game_info[0],game_info[1],game_info[2],game_info[3],game_info[4],game_info[5])
            response = game_obj.get_game_as_rec(requester)
        except Exception as e:
            response = "Could not retrieve random game"
            logging.exception(e)
        return response

    # Uses: DB
    # Responds to: req genre
    def get_genre_game(self, game_genre, requester):
        try:
            game_info = self.PG_WRAPPER.get_rows(f"SELECT name, slug, platforms, genres, stores, released, rating FROM gd.games g WHERE g.id = (SELECT vg.id FROM gd.v_games vg WHERE vg.genres LIKE '%{game_genre.lower()}%' ORDER BY RANDOM() LIMIT 1);")[0]
            game_obj = Game(game_info[0],game_info[1],game_info[2],game_info[3],game_info[4],game_info[5])
            response = game_obj.get_game_as_rec(requester)
        except Exception as e:
            genres = (self.PG_WRAPPER.get_rows("SELECT STRING_AGG(DISTINCT genres,', ') FROM gd.games WHERE genres NOT LIKE '%,%' AND genres NOT LIKE ''")[0][0])
            response = f"""Could not retrieve game by genre !\nExisting genres: {genres}"""
        return response

    # Uses: RAWG API
    # Responds to: req (with user)
    def fetch_game_rec(self, game_name, requester, mention):
        try:
            rawg_game = RawgGame(self.RAWG_API.getGame(game_name))
            response = rawg_game.get_req_game_str(requester, mention)
        except Exception as e:
            response = "Could not retrieve user recommended game"
            logging.exception(e)
        return response

    # Uses: DB, RAWG API
    # Responds to: req (with game)
    def fetch_req_game(self, game_name, requester):
        try:
            rawg_game = RawgGame(self.RAWG_API.getGame(game_name))
            response = rawg_game.get_req_game_str(requester)
        except Exception as e:
            response = "Could not retrieve requested game, if you're sure it exists, try to be more explicit !"
            logging.exception(e)
        return response

    # Uses: DB, RAWG API
    # Responds to: rate
    def rate_game(self, requester, rating, game_name):
        # check rating is valid
        if (isinstance(rating,str)) or (rating > 5 or rating < 1):
            return "Only numerical ratings between 0 & 5 accepted"

        # check user registered
        try:
            # check if user in DB
            user_idx = self.PG_WRAPPER.get_rows(f"SELECT idx FROM gd.users WHERE username LIKE '{requester}';")[0][0]
        except IndexError:
            # register user
            self.PG_WRAPPER.query(f"INSERT INTO gd.users (platform, username) VALUES ('DISCORD', '{requester}');")
            user_idx = self.PG_WRAPPER.get_rows(f"SELECT idx FROM gd.users WHERE username LIKE '{requester}';")[0][0]

        # fetch game
        game_obj = RawgGame(self.RAWG_API.getGame(game_name))

        # register rating
        try:
            self.PG_WRAPPER.query(f"INSERT INTO gd.ratings (user_idx, game_id, rating) VALUES ({user_idx},{game_obj.id},{rating});")
            response = f"{requester} rated '{game_obj.name}' a {rating}/5"
        # in case duplicate rate
        except:
            rating = self.PG_WRAPPER.get_rows(f"SELECT rating FROM gd.ratings WHERE user_idx = {user_idx} AND game_id = {game_obj.id};")[0][0]
            response = f"{requester}, you already rated '{game_obj.name}' a {rating}/5"

        return response

    # Uses: DB
    # Responds to: list
    def list_ratings(self, requester):
        games_ratings_list = self.PG_WRAPPER.get_rows(f"SELECT r.rating, g.name FROM gd.ratings r, gd.games g, gd.users u WHERE r.user_idx = u.idx AND r.game_id = g.id AND username = '{requester}' ORDER BY r.rating DESC;")
        games_list = ''
        for game in games_ratings_list:
            games_list += f"     {game[0]}     |     {game[1]}\n"
        response = f"Your ratings list so far: \nRating     Game\n{games_list}*To unrate, type {BOT_SYMBOL}unrate (copy-paste game name from list)\n*To clear list, type {BOT_SYMBOL}ResetRatings!"
        return response

    # Uses: DB
    # Responds to: unrate
    def unrate_game(self, requester, game_name):
        try:
            self.PG_WRAPPER.query(f"DELETE FROM gd.ratings WHERE game_id IN (SELECT g.id FROM gd.ratings r, gd.games g, gd.users u WHERE r.user_idx = u.idx AND r.game_id = g.id AND u.username = '{requester}' AND g.name = '{game_name}');")
            response = f"Deleted your rating for '{game_name}' !"
        except:
            response = f"{requester}, you have not rated '{game_name}' yet !"
        return response

    # Uses: DB
    # Responds to: ResetRatings!
    def reset_ratings(self, requester):
        try:
            self.PG_WRAPPER.query(f"DELETE FROM gd.ratings rs WHERE rs.idx IN (SELECT r.idx FROM gd.users u INNER JOIN gd.ratings r ON u.idx = r.user_idx WHERE u.username = '{requester}');")
            response = f"Deleted all user rating data for {requester} !"
        except:
            response = f"There is no user rating data to delete for {requester} !"
        return response

    # Uses: DB
    # Responds to: rec
    def fetch_rec_game(self, requester):
        try:
            fav_games_data = (self.PG_WRAPPER.get_rows(f"SELECT genres, released FROM gd.v_user_preferences WHERE username LIKE '{requester}';")[0])
            genres = fav_games_data[0].split(',')
            fav_genres = {i:genres.count(i) for i in genres}
            fav_genres = sorted(fav_genres, key=fav_genres.get, reverse=True)[:3]

            if len(fav_genres) == 1:
                fav_genres_str = f"genres LIKE '%{fav_genres[0]}%'"
            else:
                fav_genres_str = f"genres LIKE '%{fav_genres[0]}%'"
                for i in range(1,len(fav_genres)):
                    fav_genres_str += f" AND genres LIKE '%{fav_genres[i].strip()}%'"

            try:
                years = fav_games_data[1].split(',')
                fav_years = {i:years.count(i) for i in years}
                fav_year = sorted(fav_years, key=fav_years.get, reverse=True)[0]
            except:
                fav_year = fav_games_data[1][0]

            # fetch game
            game_info = self.PG_WRAPPER.get_rows(f"SELECT name, slug, platforms, genres, stores, released FROM gd.games g WHERE (SELECT id FROM gd.v_games vg WHERE {fav_genres_str} AND (vg.released LIKE 'None' OR INT4(vg.released) BETWEEN {int(fav_year)-5} AND {int(fav_year)+5}) AND FLOAT4(rating) > 2.5 ORDER BY RANDOM() LIMIT 1) = g.id;")[0]
            game_obj = Game(game_info[0],game_info[1],game_info[2],game_info[3],game_info[4],game_info[5])

            # return game
            response = game_obj.get_game_as_rec(requester)
        except:
            game_info = self.PG_WRAPPER.get_rows(f"SELECT name, slug, platforms, genres, stores, released, rating FROM gd.games WHERE rating > 4.5 ORDER BY RANDOM() LIMIT 1")[0]
            game_obj = Game(game_info[0],game_info[1],game_info[2],game_info[3],game_info[4],game_info[5])
            response = game_obj.get_game_as_rec(requester)
        return response

    # Uses: DB
    # Responds to: ALL
    def register_request(self, requester, request):
        self.PG_WRAPPER.query(f"INSERT INTO gd.requests (user_idx, request) VALUES ((SELECT idx FROM gd.users WHERE username LIKE '{requester}'),'{request}');")
