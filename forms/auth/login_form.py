from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, Length, ValidationError


def dut4life_email(form, field):
    if "@dut4life.ac.za" not in field.data:
        raise ValidationError("Must be a @dut4life.ac.za email address")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email(), dut4life_email])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Login")
