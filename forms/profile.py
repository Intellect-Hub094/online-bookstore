from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField
from wtforms.validators import DataRequired, Length, Optional, Email


class ProfileForm(FlaskForm):
    username = StringField(
        "Username", validators=[DataRequired(), Length(min=3, max=80)]
    )
    email = EmailField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("New Password", validators=[Optional(), Length(min=6)])
