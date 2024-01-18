from flask import Flask, render_template,redirect ,url_for, request
from forms import SignupForm,LoginForm
from dotenv import load_dotenv
import os

app = Flask(__name__)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/signup',methods=['GET','POST'])
def signup():
    form = SignupForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            userName = request.form.get("userName")
            email = request.form.get("email")
            password = request.form.get("password")
            print(f'{userName} -<>- {email} -<>- {password}')
            return redirect(url_for('home'))

    else:
        return render_template('login/signup.html',form=SignupForm())

@app.route('/login')
def login():
    return render_template('login/login.html',form=SignupForm())

app.run(port=80,debug=True)

