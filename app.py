from flask import Flask, render_template, session, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_user, LoginManager, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///predictions.db'
app.config["SECRET_KEY"] = 'mysecretkey'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(20), nullable=False)
    name = db.Column(db.String(20), nullable=False)
    authenticated = db.Column(db.Boolean, default=False)

    def is_authenticated(self):
        return self.authenticated

    def is_active(self):
        return True

    def get_id(self):
        return self.email

    def is_anonymous(self):
        return True


with app.app_context():
    db.create_all()
    db.session.commit()

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return db.session.execute(db.select(User).filter_by(id=user_id)).first()


def apology(message, status):
    return render_template("/apology.html", message=message)


@app.route('/')
@login_required
def index():
    return render_template("/index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        if not email:
            return apology("Must provide email", 403)

        if not password:
            return apology("Must provide password", 403)

        user = db.session.execute(db.select(User).filter_by(email=email)).first()
        if not user:
            return apology("User does not exist", 403)

        hashed_password = bcrypt.generate_password_hash(password)
        if hashed_password != user["User"].password:
            return apology("Wrong email/password combination", 403)

        user[0].authenticated = True

        login_user(user)
        return redirect(url_for("index"))

    return render_template("/login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
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

        user = db.session.execute(db.select(User).filter_by(email=email)).first()
        if user:
            return apology("User already exists", 403)

        hashed_password = bcrypt.generate_password_hash(password)
        user = User(name=name, email=email, password=hashed_password)
        db.session.add(user)
        db.session.commit()

        user.authenticated = True
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
