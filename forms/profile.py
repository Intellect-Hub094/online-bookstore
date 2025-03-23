from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField
from wtforms.validators import DataRequired, Length, Optional, Email

class ProfileForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired(), Email()])
    first_name = StringField("First Name", validators=[Optional(), Length(max=50)])
    last_name = StringField("Last Name", validators=[Optional(), Length(max=50)])
    password = PasswordField("New Password", validators=[Optional(), Length(min=6)])
