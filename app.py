from flask import Flask, render_template, session, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///predictions.db'
app.config["SECRET_KEY"] = 'mysecretkey'
db = SQLAlchemy(app)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(20), nullable=False)
    name = db.Column(db.String(20), nullable=False)

# # Ensure the API_KEY is set
# if not os.environ.get("API_KEY"):
#     raise RuntimeError("API_KEY not set")


# with app.app_context():
#     db.create_all()
#     db.session.commit()

def apology(message, status):
    return render_template("/login.html", message=message)


@app.route('/')
def index():
    return render_template("/login.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    session.clear()

    if request.method == "POST":
        if not request.form.get("email"):
            return apology("Please supply your email")
        elif not request.form.get("password"):
            return apology("Please supply your password")

        user = db.session.execute(db.select(User).filter_by(email=request.form.get("email")))

        if user is None:
            return apology("The user does not exist", 403)

        if generate_password_hash(request.form.get("password")) != user[0]["password"]:
            return apology("Invalid password", 403)

        session["user_id"] = user["id"]

        return redirect("/")

    else:
        return render_template("/login.html")


@app.route("/logout")
def logout():
    session.clear()

    return redirect("/login")


@app.route("/register", methods=["GET", "POST"])
def register():
    session.clear()

    if request.method == "GET":
        return render_template("/register.html")

    if request.method == "POST":
        if not request.form.get("name"):
            return apology("Must provide a name", 403)

        elif not request.form.get("email"):
            return apology("Must provide an email", 403)

        elif not request.form.get("password"):
            return apology("Must provide a poassword", 403)

        elif not request.form.get("password2"):
            return apology("Must confirm the password", 403)

        elif request.form.get("password") != request.form.get("password2"):
            return apology("Passwords do not match", 403)

        user = db.session.execute(db.select(User).filter_by(email=request.form.get("email")))

        if user is not None:
            return apology("Email already taken", 403)

        user = User(name=request.form.get("name"), email=request.form.get("email"),
                    password=generate_password_hash(request.form.get("password")))
        db.session.add(user)
        db.session.commit()
        session["user_id"] = user["id"]

        return redirect('/')


if __name__ == '__main__':
    app.debug = True
    app.run()
