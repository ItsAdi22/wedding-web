from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField,TextAreaField, DateField, URLField, SelectField, BooleanField, IntegerField
from wtforms.validators import DataRequired, Email, Length



class SignupForm(FlaskForm):
    userName = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confpassword = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class WeddingDetailsForm(FlaskForm):
    theme = SelectField('Select Theme', choices=[('template1', 'Template 1'), ('template2', 'Template 2'), ('template3', 'Template 3')], validators=[DataRequired()])
    grooms_name = StringField('Groom\'s Name', validators=[DataRequired(), Length(max=255)])
    brides_name = StringField('Bride\'s Name', validators=[DataRequired(), Length(max=255)])
    wedding_date = DateField('Wedding Date', format='%Y-%m-%d', validators=[DataRequired()])
    wedding_location = TextAreaField('Wedding Location', validators=[DataRequired(), Length(max=1000)])
    city_name = StringField('City Name of Wedding Location', validators=[DataRequired(), Length(max=255)])
    location_url = URLField('Location URL', validators=[DataRequired()])
    submit = SubmitField('Submit')

class ReservationForm(FlaskForm):
    wedding_id = IntegerField('Wedding ID', validators=[DataRequired()])
    name = StringField('Your Name', validators=[DataRequired(), Length(max=255)])
    email = StringField('Your Email', validators=[DataRequired(), Email(), Length(max=255)])
    phone = StringField('Your Phone No.', validators=[DataRequired(), Length(max=15)])  # Assuming phone number is a string
    will_attend_yes = BooleanField('Yes, I will be there')
    will_attend_no = BooleanField("Sorry, I can't come")
    note = TextAreaField('Note', validators=[Length(max=1000)])  # Adjust the max length as needed
    submit = SubmitField('Send RSVP')