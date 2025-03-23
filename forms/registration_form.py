# forms/registration_form.py
from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, PasswordField, SubmitField, SelectField, DateField, FileField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from models.user import User

class RegistrationForm(FlaskForm):
    profile_id = StringField("Profile ID", validators=[DataRequired(), Length(min=2, max=50)])
    email = EmailField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo("password")])
    profile_picture = FileField("Profile Picture")
    date_of_birth = DateField("Date of Birth", validators=[DataRequired()])
    marital_status = SelectField("Marital Status", choices=[("single", "Single"), ("married", "Married"), ("other", "Other")], validators=[DataRequired()])
    full_name = StringField("Full Name", validators=[DataRequired(), Length(min=2, max=150)])
    phone_number = StringField("Phone Number", validators=[DataRequired(), Length(min=10, max=20)])
    address = StringField("Address", validators=[DataRequired(), Length(min=2, max=250)])
    submit = SubmitField("Register")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("Email already registered. Please use a different email.")