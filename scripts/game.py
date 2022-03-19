SITE_URL = "https://rawg.io/"

class Game():
    def __init__(self,name,slug,platforms,genres,stores,released):
        self.name = name
        self.slug = slug
        self.url = SITE_URL+'games/'+self.slug
        self.platforms = platforms
        self.genres = genres
        self.stores = stores
        self.released = released

    def get_game_as_rec(self, requester):
        c_string = f"My recommendation for {requester} is: '{self.name}'\n"
        c_string += f"Genres: {self.genres}\nPlatforms: {self.platforms}\nStores: {self.stores}\nReleased date: {self.released}\nMore info: {self.url}"
        return c_string

    def get_game_as_tweet(self):
        trc_genres = ','.join(self.genres.split(',')[0:2])
        trc_stores = ','.join(self.stores.split(',')[0:2])
        trc_released = self.released.split('-')[0]
        c_string = f"I found a game called '{self.name}'. It's a: {trc_genres} game released on: {trc_released} and available on: {trc_stores}. Find more info here: {self.url}"
        return c_string

class RawgGame():
    def __init__(self, game_json):
        self.id = game_json['id']
        self.name = game_json['name']
        self.slug = game_json['slug']
        self.url = SITE_URL+'games/'+self.slug
        self.platforms = ', '.join([pf['platform']['name'] for pf in game_json['platforms']])
        self.genres = ', '.join([gr['name'] for gr in game_json['genres']])
        self.stores = ', '.join([st['store']['name'] for st in game_json['stores']])
        self.released = game_json['released']
        self.rating = game_json['rating']

    def get_req_game_str(self, requester, mention=None):
        c_string = f"Game: '{self.name}'\n"
        if mention != None:
            c_string += f"Hey {mention}, {requester} wants you to check out this game !\n"
        else:
            c_string += f"Requested by {requester}\n"
        c_string += f"Genres: {self.genres}\nPlatforms: {self.platforms}\nStores: {self.stores}\nReleased date: {self.released}\nMore info: {self.url}"
        return c_string
