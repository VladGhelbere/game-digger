#!/usr/bin/python3
import discord, os, shutil, logging
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
        {BOT_SYMBOL}req underground - request an unknown game
        {BOT_SYMBOL}req (game) - request more information about a game
        {BOT_SYMBOL}req genre (genre) - request game from a genre
        {BOT_SYMBOL}req (@user) (game) - recommend a user a game
        {BOT_SYMBOL}rec - request a game recommendation (based on your ratings)
        {BOT_SYMBOL}rate (rating) (game) - rate a game out of 5
    * Brackets content needs to be replaced by you !
'''

def get_genre_game(game_genre, requester_name):
    try:
        game_obj = rawg_wrapper.rawg_game(RAWG_API.getRandomGame(genres=game_genre))
        game_as_req = get_req_game_str(game_obj, requester_name)
        return game_as_req
    except Exception as e:
        exc = 'Could not retrieve game by genre'
        logging.exception(exc)
        return False

def get_underground_game(requester_name):
    try:
        game_obj = rawg_wrapper.rawg_game(RAWG_API.getRandomGame(order='rating'))
        game_as_req = get_req_game_str(game_obj, requester_name)
        return game_as_req
    except Exception as e:
        exc = 'Could not retrieve underground game'
        logging.exception(exc)
        return False

def fetch_random_game(requester):
    try:
        game_obj = rawg_wrapper.rawg_game(RAWG_API.getRandomGame())
        game_as_req = get_random_game_str(game_obj, requester)
        return game_as_req
    except Exception as e:
        exc = 'Could not retrieve random game'
        logging.exception(exc)
        return False

def fetch_game_rec(game_name, requester, mention):
    try:
        game_obj = rawg_wrapper.rawg_game(RAWG_API.getGame(game_name))
        game_as_req = get_req_game_str(game_obj, requester, mention)
        return game_as_req
    except Exception as e:
        exc = 'Could not retrieve user recommended game'
        logging.exception(exc)
        return False

def fetch_req_game(game_name, requester_name):
    try:
        game_obj = rawg_wrapper.rawg_game(RAWG_API.getGame(game_name))
        game_as_req = get_req_game_str(game_obj, requester_name)
        return game_as_req
    except Exception as e:
        exc = 'Could not retrieve requested game'
        logging.exception(exc)
        return False

def check_user_registered(requester):
    try:
        # check if user in DB
        user_idx = PG_WRAPPER.get_rows(f"SELECT idx FROM gd.users WHERE username LIKE '{requester}';")[0][0]
    except IndexError:
        # register user
        PG_WRAPPER.query(f"INSERT INTO gd.users (platform, username) VALUES ('DISCORD', '{requester}');")
        user_idx = PG_WRAPPER.get_rows(f"SELECT idx FROM gd.users WHERE username LIKE '{requester}';")[0][0]
    return user_idx

def rate_game(requester, rating, game_name):
    user_idx = check_user_registered(requester)
    # fetch game
    game_obj = rawg_wrapper.rawg_game(RAWG_API.getGame(game_name))
    # register rating
    PG_WRAPPER.query(f"INSERT INTO gd.ratings (user_idx, game_id, game_name, genre, rating) VALUES ({user_idx},{game_obj.id},'{game_obj.name}','{', '.join(game_obj.genres)}',{rating});")
    return True

def fetch_rec_game(requester):
    try:
        genres = (PG_WRAPPER.get_rows(f"SELECT genres FROM gd.user_genre_ratings WHERE username LIKE '{requester}';")[0][0]).replace(" ", "").split(',')
        fav_genres = {i:genres.count(i) for i in genres}
        fav_genre = max(fav_genres, key=fav_genres.get)
        game_obj = rawg_wrapper.rawg_game(RAWG_API.getRandomGame(genres=fav_genre))
        return get_rec_game_str(game_obj, requester)
    except:
        return f"I don't have enough information to make a recommendation, {requester} !\nRate some titles !"


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
        elif rate_game(author, rating, game_name):
            message_text = f"{author} rated {game_name} a {rating}/5"

    elif msg.startswith(BOT_SYMBOL+'rec'):
        message_text = fetch_rec_game(author)

    if message_text != None:
        await message.channel.send(message_text)


client.run(os.getenv('DISCORD_BOT_TOKEN'))
