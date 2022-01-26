#!/usr/bin/python3
import discord, os, logging, random, re
import lib.rawg_wrapper as rawg_wrapper
import lib.postgres_wrapper as postgres_wrapper
from utils import *

logging.basicConfig(filename=f"{os.getenv('LOG_PATH')}discord-client.log",
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S")

RAWG_API = rawg_wrapper.rawg_wrapper()
PG_WRAPPER = postgres_wrapper.DB()
client = discord.Client()
BOT_SYMBOL = os.getenv("BOT_SYMBOL")
INSTRUCTIONS = f'''
    Available Commands:
        {BOT_SYMBOL}game - recommends random game
        {BOT_SYMBOL}req (game) - request more information about a game
        {BOT_SYMBOL}req genre (genre) - request game from a genre
        {BOT_SYMBOL}req (@user) (game) - recommend a user a game
        {BOT_SYMBOL}rec - request a game recommendation (based on your ratings)
        {BOT_SYMBOL}rate (rating) (game) - rate a game out of 5
    * Brackets content needs to be replaced by you !
'''

# DB
def get_genre_game(game_genre, requester):
    try:
        game_info = PG_WRAPPER.get_rows(f"SELECT name, slug, platforms, genres, stores, released, rating FROM gd.games g WHERE g.id = (SELECT vg.id FROM gd.v_games vg WHERE vg.genres LIKE '%{game_genre.lower()}%' ORDER BY RANDOM() LIMIT 1);")[0]
        game_obj = Game(game_info[0],game_info[1],game_info[2],game_info[3],game_info[4],game_info[5])
        response = game_obj.get_game_as_rec(requester)
    except Exception as e:
        genres = (PG_WRAPPER.get_rows("SELECT STRING_AGG(DISTINCT genres,', ') FROM gd.games WHERE genres NOT LIKE '%,%' AND genres NOT LIKE ''")[0][0])
        response = f"""Could not retrieve game by genre !\nExisting genres: {genres}"""
    return response

# DB
def fetch_random_game(requester):
    try:
        game_info = PG_WRAPPER.get_rows("SELECT name, slug, platforms, genres, stores, released, rating  FROM gd.games  ORDER BY RANDOM() LIMIT 1")[0]
        game_obj = Game(game_info[0],game_info[1],game_info[2],game_info[3],game_info[4],game_info[5])
        response = game_obj.get_game_as_rec(requester)
    except Exception as e:
        response = 'Could not retrieve random game'
        logging.exception(e)
    return response

# RAWG API
def fetch_game_rec(game_name, requester, mention):
    try:
        game_obj = rawg_wrapper.rawg_game(RAWG_API.getGame(game_name))
        game_as_req = get_req_game_str(game_obj, requester, mention)
        return game_as_req
    except Exception as e:
        exc = 'Could not retrieve user recommended game'
        logging.exception(exc)
        return False

# RAWG API
def fetch_req_game(game_name, requester):
    try:
        game_obj = rawg_wrapper.rawg_game(RAWG_API.getGame(game_name))
        game_as_req = get_req_game_str(game_obj, requester)
        return game_as_req
    except Exception as e:
        exc = 'Could not retrieve requested game'
        logging.exception(exc)
        return False

# DB
def check_user_registered(requester):
    try:
        # check if user in DB
        user_idx = PG_WRAPPER.get_rows(f"SELECT idx FROM gd.users WHERE username LIKE '{requester}';")[0][0]
    except IndexError:
        # register user
        PG_WRAPPER.query(f"INSERT INTO gd.users (platform, username) VALUES ('DISCORD', '{requester}');")
        user_idx = PG_WRAPPER.get_rows(f"SELECT idx FROM gd.users WHERE username LIKE '{requester}';")[0][0]
    return user_idx

# RAWG API
def rate_game(requester, rating, game_name):
    user_idx = check_user_registered(requester)
    # fetch game
    game_obj = rawg_wrapper.rawg_game(RAWG_API.getGame(game_name))
    # register rating
    try:
        PG_WRAPPER.query(f"""INSERT INTO gd.ratings (user_idx, game_id, rating) VALUES ({user_idx},{game_obj.id},{rating});""")
        return f"{requester} rated '{game_obj.name}' a {rating}/5"
    # in case duplicate rate
    except:
        rating = PG_WRAPPER.get_rows(f"SELECT rating FROM gd.ratings WHERE user_idx = {user_idx} AND game_id = {game_obj.id};")[0][0]
        return f"{requester}, you already rated '{game_obj.name}' a {rating}/5"

# DB
def fetch_rec_game(requester):
    try:
        fav_games_data = (PG_WRAPPER.get_rows(f"SELECT genres, released, platforms FROM gd.v_user_preferences WHERE username LIKE '{requester}';")[0])
        genres = fav_games_data[0].split(',')
        fav_genres = {i:genres.count(i) for i in genres}
        fav_genres = sorted(fav_genres, key=fav_genres.get, reverse=True)[:2]

        try:
            fav_year = fav_games_data[1].split(',')[0]
        except:
            fav_year = fav_games_data[1][0]

        # fetch game
        game_info = PG_WRAPPER.get_rows(f"SELECT name, slug, platforms, genres, stores, released FROM gd.games g WHERE (SELECT id FROM gd.v_games vg WHERE genres LIKE '%{fav_genres[0]}%{fav_genres[1]}%' AND (INT4(released) BETWEEN {int(fav_year)-5} AND {int(fav_year)+5}) ORDER BY RANDOM() LIMIT 1) = g.id;")[0]
        game_obj = Game(game_info[0],game_info[1],game_info[2],game_info[3],game_info[4],game_info[5])

        # return game
        return game_obj.get_game_as_rec(requester)
    except:
        return f"I don't have enough information to make a recommendation, {requester} !\nRate some titles you enjoyed !"


@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    if message.author == client.user or message.content[0] != BOT_SYMBOL:
        return

    logging.info(message)
    message_text = None
    author = message.author.mention
    msg = message.content

    if msg.startswith(BOT_SYMBOL+'help'):
        await message.channel.send(INSTRUCTIONS)

    elif msg.startswith(BOT_SYMBOL+'game'):
        message_text = fetch_random_game(author)

    elif msg.startswith(BOT_SYMBOL+'req'):
        req_spec = msg.split(' ', 1)[1]

        if req_spec == 'underground':
            message_text = get_underground_game(author)
        elif req_spec.startswith('genre'):
            genre = req_spec.split(' ', 1)[1]
            message_text = get_genre_game(genre, author)
        elif '<@!' in req_spec[0:3]:
            user_id = req_spec.split(' ')[0]
            game_name = req_spec.split(' ')[1]
            message_text = fetch_game_rec(game_name, author, user_id)
        else:
            message_text = fetch_req_game(req_spec, author)

    elif msg.startswith(BOT_SYMBOL+'rate'):
        req_spec = msg.split(' ',2)
        rating = int(req_spec[1])
        game_name = req_spec[2]
        if isinstance(rating,str) or rating > 5:
            message_text = "Only ratings between 0 & 5 accepted"
        else:
            rate_resp = rate_game(author, rating, game_name)
            if rate_resp:
                message_text = rate_resp
            else:
                message_text = f"Failed to rate '{game_name}'"

    elif msg.startswith(BOT_SYMBOL+'rec'):
        message_text = fetch_rec_game(author)

    if message_text != None:
        await message.channel.send(message_text)


client.run(os.getenv('DISCORD_BOT_TOKEN'))

