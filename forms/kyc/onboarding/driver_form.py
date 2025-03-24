from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FileField, BooleanField, PasswordField
from wtforms.validators import DataRequired, Email, EqualTo, Length
from flask_wtf.file import FileRequired, FileAllowed

class DriverOnboardingForm(FlaskForm):
    first_name = StringField("First Name", validators=[DataRequired()])
    last_name = StringField("Last Name", validators=[DataRequired()])
    phone = StringField("Phone Number", validators=[DataRequired()])
    license_number = StringField("Driver's License Number", validators=[DataRequired()])
    vehicle_info = StringField("Vehicle Information", validators=[DataRequired()])
    license_image = FileField("Upload Driver's License Image", validators=[
        FileRequired(),
        FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')
    ])
    terms = BooleanField("I agree to the Terms and Conditions", validators=[DataRequired()])
    submit = SubmitField("Submit")
