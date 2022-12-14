import os

from flask import render_template, request, url_for, redirect
from flask_login import login_user, logout_user, current_user, login_required

from app import app, login_manager, db, bcrypt
from app.models import User, Prediction, Game
from app.forms import RegisterForm, LoginForm, PredictionForm
from app.helpers import update_db

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
    predictions_made = db.session.execute(
        db.select(Prediction, Game).join(Game.predictions).where(
            Prediction.user_id == user_id
            and Prediction.made
        ).order_by(
            Game.date.desc()).limit(10)).scalars()

    predictions_to_make = db.session.execute(
        db.select(Prediction, Game).join(Game.predictions).where(
            Prediction.user_id == user_id
            and not Game.finished
            and not Prediction.made
        )
    ).first()

    next_prediction = None

    if predictions_to_make:
        next_prediction = {
            "game_id": predictions_to_make[0].game_id,
            "user_id": predictions_to_make[0].user_id,
            "team1": predictions_to_make[0].team1,
            "team2": predictions_to_make[0].team2
        }


    form = PredictionForm()

    return render_template("/dashboard.html", predictions=predictions_made, form=form,
                           next_prediction=next_prediction)


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


@app.route("/prediction", methods=["GET", "POST"], endpoint='prediction')
@login_required
def prediction():
    if request.method == "POST":

        return apology("Not implemented", 200)
