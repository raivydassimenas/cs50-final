import requests
from datetime import date
from app import config, db
from app.models import Game

url = "https://api-nba-v1.p.rapidapi.com/games"

querystring = {"date": str(date.today())}

headers = {
    "X-RapidAPI-Key": config.API_NBA_KEY,
    "X-RapidAPI-Host": "api-nba-v1.p.rapidapi.com"
}


def get_games():
    response = requests.request("GET", url, headers=headers, params=querystring)

    response = response.json()

    finished_games = []
    upcoming_games = []

    for game in response["response"]:
        team1 = game["teams"]["visitors"]["nickname"]
        team2 = game["teams"]["home"]["nickname"]
        game_date = date.today()
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

    return finished_games, upcoming_games


def update_db():
    finished_games, upcoming_games = get_games()

    for game in finished_games:
        game_db = db.session.execute(
            db.select(Game).where(
                Game.team1 == game["team1"] and Game.team2 == game["team2"] and Game.date == game["date"])
        ).first()
        if not game_db:
            game_to_insert = Game(team1=game["team1"], score1=game["score1"], team2=game["team2"],
                                  score2=game["score2"],
                                  date=game["date"], finished=True)
            db.session.add(game_to_insert)
            db.session.commit()
        elif not game_db[0].finished:
            game_db.finished = True
            game_db.score1 = game["score1"]
            game_db.score2 = game["score2"]
            db.session.commit()

    for game in upcoming_games:
        game_db = db.session.execute(
            db.select(Game).where(
                Game.team1 == game["team1"] and Game.team2 == game["team2"] and Game.date == game["date"])
        ).first()
        if not game_db:
            game_to_insert = Game(team1=game["team1"], team2=game["team2"], date=game["date"])
            db.session.add(game_to_insert)
            db.session.commit()
