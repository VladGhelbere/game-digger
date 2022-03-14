#!/usr/bin/python3
import discord, os, logging
import recommender

logging.basicConfig(filename=f"{os.getenv('LOG_PATH')}discord-client.log",
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S")

recommender = recommender.GameRecommender()
client = discord.Client()
BOT_SYMBOL = os.getenv("BOT_SYMBOL")
INSTRUCTIONS = f"""
    Available Commands:
        {BOT_SYMBOL}game - recommends random game
        {BOT_SYMBOL}req (game) - request more information about a game
        {BOT_SYMBOL}req genre (genre) - request game from a genre
        {BOT_SYMBOL}req (@user) (game) - recommend a user a game
        {BOT_SYMBOL}rec - request a game recommendation (based on your ratings)
        {BOT_SYMBOL}rate (rating) (game) - rate a game out of 5
        {BOT_SYMBOL}list - list games rated so far
        {BOT_SYMBOL}unrate (game-name from $list) - delete rating for a game
        {BOT_SYMBOL}ResetRatings! - resets all games rated so far
    * Brackets content needs to be replaced by you !
"""


@client.event
async def on_ready():
    print("Logged in as {0.user}".format(client))


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
        message_text = recommender.fetch_random_game(author)

    elif msg.startswith(BOT_SYMBOL+'req'):
        req_spec = msg.split(' ', 1)[1]

        if req_spec.startswith('genre'):
            genre = req_spec.split(' ', 1)[1]
            message_text = recommender.get_genre_game(genre, author)
        elif '<@!' in req_spec[0:3]:
            user_id = req_spec.split(' ')[0]
            game_name = req_spec.split(' ')[1]
            message_text = recommender.fetch_game_rec(game_name, author, user_id)
        else:
            message_text = recommender.fetch_req_game(req_spec, author)

    # rate a title
    elif msg.startswith(BOT_SYMBOL+'rate'):
        req_spec = msg.split(' ',2)
        rating = int(req_spec[1])
        game_name = req_spec[2]
        message_text = recommender.rate_game(author, rating, game_name)

    # ask for a recommendation
    elif msg.startswith(BOT_SYMBOL+'rec'):
        message_text = recommender.fetch_rec_game(author)

    # list rated games
    elif msg.startswith(BOT_SYMBOL+'list'):
        message_text = recommender.list_ratings(author)

    # unrate a game
    elif msg.startswith(BOT_SYMBOL+'unrate'):
        game_name = msg.split(' ', 1)[1]
        message_text = recommender.unrate_game(author, game_name)

    # resets ratings for a user
    elif msg.startswith(BOT_SYMBOL+'ResetRatings!'):
        message_text = recommender.reset_ratings(author)

    if message_text != None:
        await message.channel.send(message_text)
        recommender.register_request(author, msg)

client.run(os.getenv("DISCORD_BOT_TOKEN"))
