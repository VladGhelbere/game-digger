#!/usr/bin/python3
import requests, json
from time import sleep
import lib.rawg_wrapper as rawg_wrapper
import lib.postgres_wrapper as postgres_wrapper

RAWG_API = rawg_wrapper.rawg_wrapper()
PG_WRAPPER = postgres_wrapper.DB()

result = RAWG_API.api_request(params={'page_size':40,'ordering':'-rating'})
# result = requests.get("https://api.rawg.io/api/games?key=1923224357cf4254bf3ced8b39864b21&ordering=-rating&page=9259&page_size=40").json()

while True:
        next_page = result["next"]
        print(next_page)
        results = result["results"]
        for game in results:
                game_obj = rawg_wrapper.rawg_game(game)
                print(game_obj.name)
                try:
                        # TO:DO - add check to see if game already exists, after cloning the DB
                        PG_WRAPPER.query(f"""INSERT INTO gd.games (id, name, slug, platforms, genres, stores, released, rating) VALUES ({game_obj.id},'{game_obj.name.replace("'"," ")}','{game_obj.slug}','{','.jo>
                except:
                        continue
        result = requests.get(next_page).json()
        sleep(1)
        if next_page is None or next_page == "null":
                break

