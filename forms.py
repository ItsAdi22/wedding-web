from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, Form,TextAreaField, DateField, URLField, SelectField
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