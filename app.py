from flask import Flask, render_template, session, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_user, LoginManager, login_required, logout_user, current_user, UserMixin
from flask_bcrypt import Bcrypt
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Email

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///predictions.db'
app.config["SECRET_KEY"] = 'mysecretkey'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    name = db.Column(db.String(20), nullable=False)


with app.app_context():
    db.create_all()
    db.session.commit()


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()], render_kw={"placeholder": "Email"})
    password = PasswordField("Password", validators=[DataRequired()], render_kw={"placeholder": "Password"})
    submit = SubmitField("Login")


class RegisterForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()], render_kw={"placeholder": "Name"})
    email = StringField("Email", validators=[DataRequired(), Email()], render_kw={"placeholder": "Email"})
    password = PasswordField("Password", validators=[DataRequired()], render_kw={"placeholder": "Password"})
    password2 = PasswordField("Confirm password", validators=[DataRequired()],
                              render_kw={"placeholder": "Confirm password"})
    submit = SubmitField("Register")


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return db.session.execute(db.select(User).filter_by(id=user_id)).first()[0]


def apology(message, status, password1=None, password2=None):
    return render_template("/apology.html", message=message, password1=password1, password2=password2)


@app.route('/')
@login_required
def index():
    return render_template("/index.html")


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

        login_user(user)
        return redirect(url_for("index"))

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

            login_user(user)

            return redirect(url_for("index"))

    return render_template("/register.html", form=form)


@app.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()

    return redirect(url_for("login"))


if __name__ == '__main__':
    app.debug = True
    app.run()
