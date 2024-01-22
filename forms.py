from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField,TextAreaField, DateField, URLField, SelectField, RadioField, IntegerField, EmailField, FileField
from wtforms.validators import DataRequired, Email, Length
from flask_wtf.file import FileRequired



class SignupForm(FlaskForm):
    userName = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confpassword = PasswordField('Confirm Password', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class WeddingDetailsForm(FlaskForm):
    theme = SelectField('Select Theme', choices=[('template1', 'Template 1'), ('template2', 'Template 2'), ('template3', 'Template 3')], validators=[DataRequired()])
    grooms_name = StringField('Groom\'s Name', validators=[DataRequired(), Length(max=255)])
    brides_name = StringField('Bride\'s Name', validators=[DataRequired(), Length(max=255)])
    wedding_date = DateField('Wedding Date', format='%Y-%m-%d', validators=[DataRequired()])
    wedding_location = TextAreaField('Wedding Location', validators=[DataRequired(), Length(max=500)])
    city_name = StringField('City Name of Wedding Location', validators=[DataRequired(), Length(max=255)])
    location_url = URLField('Location URL', validators=[DataRequired()])
    submit = SubmitField('Submit')

class ReservationForm(FlaskForm):
    wedding_id = IntegerField('Wedding ID', validators=[DataRequired()])
    name = StringField('Your Name', validators=[DataRequired(), Length(max=255)])
    email = EmailField('Your Email', validators=[DataRequired(), Email(), Length(max=255)])
    phone = IntegerField('Your Phone No.', validators=[DataRequired(), Length(max=10)])  # Assuming phone number is a string
    will_attend = RadioField('Will you attend?', choices=[('1', 'Yes, I will be there'), ('0', "Sorry, can't come")], default='1')
    note = TextAreaField('Note', validators=[Length(max=500)])  # Adjust the max length as needed
    submit = SubmitField('Send RSVP')

class CoupleImageForm(FlaskForm):
    groom = FileField('Groom Image', validators=[DataRequired()])
    bride = FileField('Bride Image', validators=[DataRequired()])
    submit = SubmitField('Upload')