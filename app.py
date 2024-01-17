from flask import Flask, render_template,redirect ,url_for

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/signup')
def signup():
    return render_template('login/signup.html')

app.run(port=80,debug=True)

