from flask import Flask, render_template,redirect ,url_for

app = Flask(__name__)

@app.get('/')
def home():
    return render_template('home.html')
app.run(port=80,debug=True)