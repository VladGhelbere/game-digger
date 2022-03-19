#!/usr/bin/python3
import requests, json
from time import sleep
import lib.rawg_wrapper as rawg_wrapper
import lib.postgres_wrapper as postgres_wrapper
import game

RAWG_API = rawg_wrapper.rawg_wrapper()
PG_WRAPPER = postgres_wrapper.DB()
DB_TABLE_NAME = 'gd.temp_games'

results = RAWG_API.api_request(params={'page_size':40,'ordering':'-rating'})
# results = requests.get("https://api.rawg.io/api/games?key=1923224357cf4254bf3ced8b39864b21&ordering=-rating&page=9259&page_size=40").json()

while True:
        next_page = results["next"]
        print(next_page)
        result = results["results"]
        for game_json in result:
                try:
                        game_obj = game.RawgGame(game_json)
                        PG_WRAPPER.query(f"""INSERT INTO {DB_TABLE_NAME} (id, name, slug, platforms, genres, stores, released, rating) VALUES ({game_obj.id},'{game_obj.name.replace("'"," ")}','{game_obj.slug}','{game_obj.platforms}','{game_obj.genres}','{game_obj.stores}','{game_obj.released}',{game_obj.rating})""")
                except:
                        continue
        results = requests.get(next_page).json()
        sleep(0.5)
        if len(results) < 2:
                break
