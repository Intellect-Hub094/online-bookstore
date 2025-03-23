# forms/profile_form.py
from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, DateField, SelectField, FileField, SubmitField
from wtforms.validators import DataRequired, Email, Length

class ProfileForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired(), Email()])
    profile_picture = FileField("Profile Picture")
    date_of_birth = DateField("Date of Birth", validators=[DataRequired()])
    marital_status = SelectField("Marital Status", choices=[("single", "Single"), ("married", "Married"), ("other", "Other")], validators=[DataRequired()])
    full_name = StringField("Full Name", validators=[DataRequired(), Length(min=2, max=150)])
    phone_number = StringField("Phone Number", validators=[DataRequired(), Length(min=10, max=20)])
    address = StringField("Address", validators=[DataRequired(), Length(min=2, max=250)])
    submit = SubmitField("Update Profile")