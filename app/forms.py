from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, IntegerField
from wtforms.validators import DataRequired, Email


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


class PredictionForm(FlaskForm):
    pscore1 = IntegerField("Score 1", validators=[DataRequired()])
    pscore2 = IntegerField("Score 2", validators=[DataRequired()])
    submit = SubmitField("Submit score")
