from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import StringField, PasswordField, EmailField, SubmitField, FileField
from wtforms.validators import DataRequired, Length, Optional, Email


class ProfileForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired(), Email()])
    first_name = StringField("First Name", validators=[Optional(), Length(max=50)])
    last_name = StringField("Last Name", validators=[Optional(), Length(max=50)])
    password = PasswordField("New Password", validators=[Optional(), Length(min=6)])
    confirm_password = PasswordField(
        "Confirm New Password", validators=[Optional(), Length(min=6)]
    )
    phone = StringField("Phone Number", validators=[Optional(), Length(max=15)])
    address = StringField("Delivery Address", validators=[Optional(), Length(max=255)])
    student_id = StringField("Student ID", validators=[Optional(), Length(max=50)])
    license_number = StringField(
        "Driver's License Number", validators=[Optional(), Length(max=50)]
    )
    vehicle_info = StringField(
        "Vehicle Information", validators=[Optional(), Length(max=255)]
    )
    license_image = FileField(
        "Upload Driver's License Image",
        validators=[Optional(), FileAllowed(["jpg", "png", "jpeg"], "Images only!")],
    )
    submit = SubmitField("Update Profile")
