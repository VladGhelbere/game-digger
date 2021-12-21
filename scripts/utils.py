def get_random_game_str(game_obj, requester):
    c_string = f"Hey {requester}, here's a random game: '{game_obj.name}'\n"

    if game_obj.genres != []:
        c_string += f"Genres: {', '.join(game_obj.genres)}\n"
    if game_obj.platforms != []:
        c_string += f"Platforms: {', '.join(game_obj.platforms)}\n"
    if game_obj.release_date != None:
        c_string += f"Released date: {game_obj.release_date}\n"
    if game_obj.url != None:
        c_string += f"More info: {game_obj.url}"

    return c_string

def get_rec_game_str(game_obj, requester):
    c_string = f"My recommendation for {requester} is: '{game_obj.name}'\n"

    if game_obj.genres != []:
        c_string += f"Genres: {', '.join(game_obj.genres)}\n"
    if game_obj.platforms != []:
        c_string += f"Platforms: {', '.join(game_obj.platforms)}\n"
    if game_obj.release_date != None:
        c_string += f"Released date: {game_obj.release_date}\n"
    if game_obj.url != None:
        c_string += f"More info: {game_obj.url}"

    return c_string

def get_req_game_str(game_obj, requester, mention=None):
    c_string = f"Game: '{game_obj.name}'\n\n"
    if mention != None:
        c_string += f"Hey {mention}, {requester} wants you to check out this game !\n"
    else:
        c_string += f"Requested by {requester}\n"

    if game_obj.genres != []:
        c_string += f"Genres: {', '.join(game_obj.genres)}\n"

    if game_obj.platforms != []:
        c_string += f"Platforms: {', '.join(game_obj.platforms)}\n"

    if game_obj.release_date != None:
        c_string += f"Released date: {game_obj.release_date}\n"

    if game_obj.user_rating != 0:
        c_string += f"User Rating: {game_obj.user_rating}/5\n"

    if game_obj.metacritic != None:
        c_string += f"Metacritic: {game_obj.metacritic}/100\n"

    if game_obj.stores != []:
        c_string += f"Stores: {', '.join(game_obj.stores)}\n"

    if game_obj.url != None:
        c_string += "More info: "+game_obj.url

    return c_string
