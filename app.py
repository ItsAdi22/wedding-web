from flask import Flask, render_template,redirect ,url_for, request, flash
from flask_mysqldb import MySQL
from forms import SignupForm,LoginForm
from dotenv import load_dotenv
import os

app = Flask(__name__)
mysql = MySQL(app)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

app.config["MYSQL_HOST"] = os.getenv('MYSQL_HOST')
app.config["MYSQL_DB"] = os.getenv('MYSQL_DB')
app.config["MYSQL_USER"] = os.getenv('MYSQL_USER')
app.config["MYSQL_PASSWORD"] = os.getenv('MYSQL_PASSWORD')


def createtables():
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS users ( id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255) NOT NULL, email VARCHAR(255) NOT NULL UNIQUE, password VARCHAR(255) NOT NULL );")

    except Exception as e:
        print(f"ERROR OCCURRED: {e}")
        return redirect(url_for('home'))
    
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/signup',methods=['GET','POST'])
def signup():
    createtables()
    form = SignupForm()
    if form.validate_on_submit():
            userName = request.form.get("userName")
            email = request.form.get("email")
            password = request.form.get("password")

            try:
                cursor = mysql.connection.cursor()
                cursor.execute('SELECT * FROM users WHERE email = %s',(email,))
                account = cursor.fetchone()
            
            except Exception as e:
                print(f"ERROR OCCURRED: {e}")
                return redirect(url_for('home'))

            else:
                account = cursor.fetchone()
                if account:
                    flash("Email already used! Please use different email address")
                    return render_template('login/signup.html')   
                
                else:
                    sql = "INSERT INTO users (name,email,password) VALUES(%s,%s,%s)"
                    value = (userName,email,password)
                    cursor.execute(sql,value)
                    mysql.connection.commit()
                    cursor.close() 
                    flash("User Registration Successful!")
                    return redirect(url_for('signup'))
    else:
        return render_template('login/signup.html',form=SignupForm())

@app.route('/login',methods=['POST','GET'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = request.form.get("email")
        password = request.form.get("password")
        return "Login Successful"
    
    else:
        return render_template('login/login.html',form=LoginForm())

app.run(port=80,debug=True)

