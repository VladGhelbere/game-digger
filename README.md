# game-digger

### About:
This project aims to implement a recommender system for video games. The project uses a cloned games database as well as the RAWG API for the source data. The user may interact with the system throughout bots that will be available on several platforms. The users will be able to rate games & request recommendations from the system.

The project uses two docker containers: a PostgreSQL DB & the python code.

---- ----

### Unique Features:

- You can recommend your friends a game.
- You can rate games & get recommendations based on the games you rated.
- Recommendations are made based on genres & published year.

---- ----

### Available on the following platforms:
- [x] Discord
- [ ] Twitter
- [ ] Facebook

---- ----

### Available Commands:

  - $help - request full list of commands
  - $game - recommends random game
  - $req (game) - request more information about a game
  - $req genre (genre) - request game from a genre
  - $req (@user) (game) - recommend a user a game
  - $rec - request a game recommendation (based on your ratings)
  - $rate (rating) (game) - rate a game out of 5 
  - $list - list games rated so far
  - $unrate (game-name from $list) - delete rating for a game
  - $ResetRatings! - resets all games rated so far


##### Brackets content needs to be replaced by you !

---- ----
