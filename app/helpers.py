import requests
from datetime import datetime, date, timedelta
from app import config, db
from app.models import Game, Prediction, User

url = "https://api-nba-v1.p.rapidapi.com/games"

headers = {
    "X-RapidAPI-Key": config.API_NBA_KEY,
    "X-RapidAPI-Host": "api-nba-v1.p.rapidapi.com"
}


def get_games(querystring):
    response = requests.request("GET", url, headers=headers, params=querystring)

    response = response.json()

    finished_games = []
    upcoming_games = []

    for game in response["response"]:
        team1 = game["teams"]["visitors"]["nickname"]
        team2 = game["teams"]["home"]["nickname"]
        if game["status"]["short"] == 3:
            score1 = game["scores"]["visitors"]["points"]
            score2 = game["scores"]["home"]["points"]
            if game["date"]["end"]:
                game_date = datetime.fromisoformat(game["date"]["end"])
            else:
                game_date = querystring["date"]
            game_obj = {
                "team1": team1,
                "team2": team2,
                "score1": score1,
                "score2": score2,
                "date": game_date
            }
            finished_games.append(game_obj)
        else:
            game_date = querystring["date"]
            game_obj = {
                "team1": team1,
                "team2": team2,
                "date": game_date
            }
            upcoming_games.append(game_obj)

    return finished_games, upcoming_games


def update_db():
    last_access_date = db.session.execute(
        db.select(Access)
    )
    finished_games, upcoming_games = get_games(querystring = {"date": str(date.today())})
    finished_games1, upcoming_games1 = get_games({"date": str(date.today() + timedelta(days=1))})
    upcoming_games.extend(upcoming_games1)

    for game in finished_games:
        game_db = db.session.execute(
            db.select(Game).where(
                Game.team1 == game["team1"] and Game.team2 == game["team2"] and Game.date.date() == game["date"].date())
        ).first()
        if not game_db:
            game_to_insert = Game(team1=game["team1"], score1=game["score1"], team2=game["team2"],
                                  score2=game["score2"],
                                  date=game["date"], finished=True)
            db.session.add(game_to_insert)
            db.session.commit()
        elif not game_db[0].finished:
            db.session.execute(db.update(Game).where(
                Game.id == game["id"]
            ).values(finished=True, score1=game["score1"], score2=game["score2"], date=game["date"]))

    for game in upcoming_games:
        game_db = db.session.execute(
            db.select(Game).where(
                Game.team1 == game["team1"] and Game.team2 == game["team2"] and Game.date.date() == game["date"].date() )
        ).first()
        if not game_db:
            game_to_insert = Game(team1=game["team1"], team2=game["team2"], date=game["date"])
            db.session.add(game_to_insert)
            db.session.commit()

def calculate_points_per_game(score1, score2, pscore1, pscore2):
    points = 0
    if score1 > score2 and pscore1 > pscore2:
        points += 20 + abs((score1 - score2) - (pscore1 - pscore2))
        points = points if points > 0 else 0
    elif score1 < score2 and pscore2 < pscore2:
        points += 20 + abs((score2 - score1) - (pscore2 - pscore1))
        points = points if points > 0 else 0
    return points

def calculate_points(user_id):
    points_to_add = 0
    predictions_to_calculate = db.session.execute(
        db.select(Game, Prediction).join(Game.predictions).where(
            not Prediction.calculated_to_score
            and Game.finished
            and Prediction.user_id == user_id
        )
    ).scalars()
    for prediction_to_calculate in predictions_to_calculate:
        score1, score2, pscore1, pscore2 = prediction_to_calculate.score1, prediction_to_calculate.score2, prediction_to_calculate.pscore1, prediction_to_calculate.pscore2
        points_to_add += calculate_points_per_game(score1, score2, pscore1, pscore2)
        db.session.execute(db.update(Prediction).where(
            Prediction.user_id == user_id
            and Prediction.game_id == prediction_to_calculate.game_id
        ).values(calculated_to_score=True))
    points = db.session.execute(db.select(User).where(User.id == user_id)).first()[0].points
    points += points_to_add
    db.session.execute(db.update(User).where(
        User.id == user_id
    ).values(points=points))
