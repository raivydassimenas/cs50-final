import os

from flask import render_template, request, url_for, redirect
from flask_login import login_user, logout_user, current_user, login_required
from datetime import datetime

from app import app, login_manager, db, bcrypt
from app.models import User, Prediction, Game
from app.forms import RegisterForm, LoginForm, PredictionForm
from app.helpers import update_db, calculate_points

login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    user = db.session.execute(db.select(User).filter_by(id=user_id)).first()
    return user[0] if user else None


def apology(message, status, password1=None, password2=None):
    return render_template("/apology.html", message=message, password1=password1, password2=password2)


@app.route('/', endpoint='dashboard')
@login_required
def dashboard():
    user_id = current_user.id
    calculate_points(user_id)
    predictions = db.session.execute(
        db.select(Prediction).join(Game).where(
            Prediction.user_id == user_id
            and Prediction.made == True).order_by(
            Game.date.desc()).limit(10)).scalars()

    games_to_display = []

    for prediction1 in predictions:
        game = db.session.execute(
            db.select(Game).join(Prediction).where(
                Game.id == prediction1.game_id
            )
        ).first()
        game = game[0]
        game_to_display = {"team1": game.team1, "team2": game.team2, "score1": game.score1, "score2": game.score2,
                           "date": str(game.date)[:10], "pscore1": prediction1.pscore1,
                           "pscore2": prediction1.pscore2}
        games_to_display.append(game_to_display)

    unfinished_games = db.session.execute(
        db.select(Game).where(
            Game.finished == False
        )
    ).scalars()

    made_predictions = db.session.execute(
        db.select(Prediction.game_id).where(
            Prediction.made == True
            and Prediction.user_id == user_id
        )
    ).scalars()

    next_prediction = None
    curr_pred_game_id = None

    for game in unfinished_games:
        if not made_predictions or game.id not in made_predictions:
            next_prediction = {
                "game_id": game.id,
                "user_id": user_id,
                "team1": game.team1,
                "team2": game.team2
            }
            curr_pred_game_id = game.id
            break

    form = PredictionForm()

    return render_template("/dashboard.html", games_to_display=games_to_display, form=form,
                           next_prediction=next_prediction, curr_pred_game_id=curr_pred_game_id)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if request.method == "POST" and form.validate_on_submit():

        email = form.email.data
        password = form.password.data

        user = db.session.execute(db.select(User).filter_by(email=email)).first()

        if not user:
            return apology("User does not exist", 403)
        user = user[0]
        if not bcrypt.check_password_hash(user.password, password):
            return apology("Wrong email/password combination", 403)

        update_db()

        login_user(user)
        return redirect(url_for("dashboard"))

    return render_template("/login.html", form=form)


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()

    if request.method == "POST":
        if form.validate_on_submit():
            name = form.name.data
            email = form.email.data
            password = form.password.data
            password2 = form.password2.data

            if password != password2:
                return apology("Passwords do not match", 403)

            user = db.session.execute(db.select(User).filter_by(email=email)).first()
            if user:
                return apology("User already exists", 403)

            hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
            user = User(name=name, email=email, password=hashed_password)
            db.session.add(user)
            db.session.commit()

            update_db()

            login_user(user)

            return redirect(url_for("dashboard"))

    return render_template("/register.html", form=form)


@app.route("/logout", methods=["GET", "POST"], endpoint='logout')
@login_required
def logout():
    logout_user()

    return redirect(url_for("login"))


@app.route("/prediction/<int:game_id>", methods=["GET", "POST"], endpoint='prediction')
@login_required
def prediction(game_id):
    form = PredictionForm(request.form)
    if request.method == "POST" and form.validate():
        game = db.session.execute(
            db.select(Game).where(Game.id == game_id)
        ).first()
        if game:
            prediction_made = Prediction(
                pscore1=form.pscore1.data, pscore2=form.pscore2.data, user_id=current_user.id, game_id=game_id,
                created_at=datetime.now(), made=True)
            db.session.add(prediction_made)
            db.session.commit()
    return redirect(url_for("dashboard"))
