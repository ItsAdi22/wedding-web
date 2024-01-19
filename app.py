from flask import Flask, render_template,redirect ,url_for, request, flash, session
from flask_mysqldb import MySQL
from forms import SignupForm,LoginForm,WeddingDetailsForm
import os

app = Flask(__name__)
mysql = MySQL(app)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

app.config["MYSQL_HOST"] = os.getenv('MYSQL_HOST')
app.config["MYSQL_DB"] = os.getenv('MYSQL_DB')
app.config["MYSQL_USER"] = os.getenv('MYSQL_USER')
app.config["MYSQL_PASSWORD"] = os.getenv('MYSQL_PASSWORD')

@app.route('/tables')
def createtables():
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS users ( id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255) NOT NULL, email VARCHAR(255) NOT NULL, password VARCHAR(255) NOT NULL );")

    except Exception as e:
        print(f"ERROR OCCURRED: {e}")
        flash(f"ERROR OCCURRED: {e}")
        return redirect(url_for('home'))
    
@app.route('/')
def home():
    if 'email' in session:
        return render_template('home.html')
    else:
        return render_template('home.html')

###################################### ROUTES FOR LOGIN/SIGNUP START ######################################
@app.route('/signup', methods=['GET', 'POST'])
@app.route('/register', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if 'email' in session:
        return redirect(url_for('home'))
    
    else:
        if form.validate_on_submit():
            userName = request.form.get("userName")
            email = request.form.get("email")
            password = request.form.get("password")
            confpassword = request.form.get("confpassword")

            if password == confpassword:
                try:
                    cursor = mysql.connection.cursor()
                    cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
                    account = cursor.fetchone()

                except Exception as e:
                    print(f"ERROR OCCURRED: {e}")
                    return redirect(url_for('home'))

                else:
                    if account:
                        flash("Email already used! Please use a different email address")
                        return redirect(url_for('signup'))

                    else:
                        sql = "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)"
                        value = (userName, email, password)
                        cursor.execute(sql, value)
                        mysql.connection.commit()
                        cursor.close()
                        flash("User Registration Successful!")
                        return redirect(url_for('login'))
            else:
                flash("Password and confirmpassword fields should match!")
                return redirect(url_for('signup'))
        else:
            return render_template('login/signup.html', form=SignupForm())

@app.route('/login',methods=['POST','GET'])
@app.route('/signin',methods=['POST','GET'])
def login():
    form = LoginForm()
    if 'email' in session:
        return redirect(url_for('home'))
    
    else:
        if form.validate_on_submit():

            email = request.form.get("email")
            password = request.form.get("password")
            
            try:
                cursor = mysql.connection.cursor()
                
            
            except Exception as e:
                flash(f"ERROR OCCURRED: {e}")
                return redirect(url_for('home')) 
            
            else:
                cursor.execute('SELECT * FROM users WHERE email = %s AND password IS NOT NULL AND password = %s', (email, password,))
                account = cursor.fetchone()
                if account:
                    session['email'] = email
                    flash("Login Successful")
                    return redirect(url_for('home'))
                
                else:
                    flash('Incorrect Email / Password')
                    return redirect(url_for('login'))
        
        else:
            return render_template('login/login.html',form=LoginForm())
    
@app.route('/logout')
def logout():
    session.pop('email',None)
    flash("Logged Out")
    return redirect(url_for('home'))

###################################### ROUTES FOR LOGIN/SIGNUP END ######################################
@app.route('/create',methods=['POST','GET'])
def create():
    if 'email' in session:
        form = WeddingDetailsForm()
        if form.validate_on_submit():
            # Process the form data as needed
            grooms_name = request.form.get("grooms_name")
            brides_name = request.form.get("brides_name")
            wedding_date = request.form.get("wedding_date")
            wedding_location = request.form.get("wedding_location")
            city_name = request.form.get("city_name")

            flash(f'{grooms_name}-{brides_name}-{wedding_date}-{wedding_location}-{city_name}')
            print(f'{grooms_name}-{brides_name}-{wedding_date}-{wedding_location}-{city_name}')
            return redirect(request.referrer)
        
        return render_template('dashboard.html',form=form)
    else:
        return redirect(url_for('login'))

@app.route('/create/view1')
def view():
    return render_template('wedding/index.html')
app.run(port=80,debug=True)

