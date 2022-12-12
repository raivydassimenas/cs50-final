import requests
from datetime import date
from app import config, db

url = "https://api-nba-v1.p.rapidapi.com/games"

querystring = {"date": str(date.today())}

headers = {
    "X-RapidAPI-Key": config.API_NBA_KEY,
    "X-RapidAPI-Host": "api-nba-v1.p.rapidapi.com"
}

finished_games = []
upcoming_games = []

def get_games():
    response = requests.request("GET", url, headers=headers, params=querystring)

    response = response.json()

    finished_games.clear()
    upcoming_games.clear()

    for game in response["response"]:
        team1 = game["teams"]["visitors"]["nickname"]
        team2 = game["teams"]["home"]["nickname"]
        game_date = str(date.today())
        if game["status"]["short"] == 3:
            score1 = game["scores"]["visitors"]["points"]
            score2 = game["scores"]["home"]["points"]
            game_obj = {
                "team1": team1,
                "team2": team2,
                "score1": score1,
                "score2": score2,
                "date": game_date
            }
            finished_games.append(game_obj)
        else:
            game_obj = {
                "team1": team1,
                "team2": team2,
                "date": game_date
            }
            upcoming_games.append(game_obj)

