from flask import Flask, render_template, session, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
# from flask_wtf import FlaskForm
# from wtforms import StringField, PasswordField, SubmitField
# from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///predictions.db'
app.config["SECRET_KEY"] = 'mysecretkey'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(20), nullable=False)
    name = db.Column(db.String(20), nullable=False)


# class RegisterForm(FlaskForm):
#     name = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw=["placeholder", "Name"])
#     email = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw=["placeholder", "Email"])
#     password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)], render_kw=["placeholder", "Password"])
#     submit = SubmitField("Register")
#
#     def validate_email(self, email):
#         existing_user_email = db.session.execute(db.select(User).filter_by(email=email.data)).one()
#         if existing_user_email:
#             raise ValidationError("That email already exists")
#
#
# class LoginForm(FlaskForm):
#     email = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw=["placeholder", "Email"])
#     password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)], render_kw=["placeholder", "Password"])
#     submit = SubmitField("Register")


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return db.session.execute(db.select(User).filter_by(id=user_id)).one()


def apology(message, status):
    return render_template("/apology.html", message=message)

@app.route('/')
@login_required
def index():
    return render_template("/index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    # form = LoginForm()
    # if form.validate_on_submit():
    #     user = db.session.execute(db.select(User).filter_by(email=form.email.data)).one()
    #     if user:
    #         if bcrypt.check_password_hash(user.password, form.password.data):
    #             login_user(user)
    #             return redirect(url_for("index"))
    #
    # return render_template("/login.html", form=form)
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        if not email:
            return apology("Must provide email", 403)

        if not password:
            return apology("Must provide password", 403)

        user = db.session.execute(db.select(User).filter_by(email=email)).one()
        if not user:
            return apology("User does not exist", 403)

        hashed_password = bcrypt.generate_password_hash(password)
        if hashed_password != user["password"]:
            return apology("Wrong email/password combination", 403)

        login_user(user)
        return redirect(url_for("index"))

    return render_template("/login.html")




@app.route("/register", methods=["GET", "POST"])
def register():
    # form = RegisterForm()
    #
    # if form.validate_on_submit():
    #     hashed_password = bcrypt.generate_password_hash(form.password.data)
    #     new_user = User(name=form.name.data, email=form.email.data, password=hashed_password)
    #     db.session.add(new_user)
    #     db.session.commit()
    #
    #     return redirect(url_for("/"))
    #
    # return render_template("/register.html", form=form)

    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        password2 = request.form.get("password2")

        if not name:
            return apology("Must provide name", 403)

        if not email:
            return apology("Must provide email", 403)

        if not password:
            return apology("Must provide password", 403)

        if not password2:
            return apology("Must confirm password", 403)

        if password != password2:
            return apology("Passwords do not match", 403)

        user = db.session.execute(db.select(User).filter_by(email=email)).one()
        if user:
            return apology("User already exists", 403)

        hashed_password = bcrypt.generate_password_hash(password)
        user = User(name=name, email=email, password=hashed_password)
        db.session.add(user)
        db.session.commit()

        login_user(user)
        return redirect(url_for("index"))

    return render_template("/register.html")



@app.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()

    return redirect(url_for("login"))


if __name__ == '__main__':
    app.debug = True
    app.run()
