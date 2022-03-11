#!/usr/bin/python3
import os, logging
from lib.twitter_wrapper import *
import lib.postgres_wrapper as postgres_wrapper
import recommender
from game import Game

logging.basicConfig(filename=f"{os.getenv('LOG_PATH')}discord-client.log",
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S")
GLOBAL_HASHTAGS = '#videogames #gamers #gaming #bot #gamedigger'

PG_WRAPPER = postgres_wrapper.DB()
recommender = recommender.GameRecommender()
twitter_api = twitter_wrapper()

def tweet_random_game():
    game_info = PG_WRAPPER.get_rows("SELECT name, slug, platforms, genres, stores, released, rating  FROM gd.games  ORDER BY RANDOM() LIMIT 1")[0]
    game_obj = Game(game_info[0],game_info[1],game_info[2],game_info[3],game_info[4],game_info[5])
    tweet = game_obj.get_game_as_tweet() + ' ' + GLOBAL_HASHTAGS
    if (len(tweet) + len(GLOBAL_HASHTAGS)) > 280:
        tweet = game_obj.get_game_as_tweet()
    twitter_api.tweet(tweet)


def main():
    # generate post
    tweet_random_game()

    twitter_api.thank_comments()

if __name__ == "__main__":
    main()
