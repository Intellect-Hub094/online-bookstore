# forms/edit_user_form.py
from flask_wtf import FlaskForm
from wtforms import EmailField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email

class EditUserForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired(), Email()])
    is_admin = BooleanField("Is Admin")
    submit = SubmitField("Update User")