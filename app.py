from flask import Flask, render_template,redirect ,url_for, request, flash, session
from flask_mysqldb import MySQL
from forms import SignupForm,LoginForm,WeddingDetailsForm,ReservationForm
import os
import random

app = Flask(__name__)
mysql = MySQL(app)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

app.config["MYSQL_HOST"] = os.getenv('MYSQL_HOST')
app.config["MYSQL_DB"] = os.getenv('MYSQL_DB')
app.config["MYSQL_USER"] = os.getenv('MYSQL_USER')
app.config["MYSQL_PASSWORD"] = os.getenv('MYSQL_PASSWORD')

#generate wedding id
def generate_random_code():
    return str(random.randint(10000, 99999))


@app.route('/tables')
def createtables():
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS users ( id INTEGER PRIMARY KEY AUTO_INCREMENT, wedding_id INTEGER, name VARCHAR(255) NOT NULL, email VARCHAR(255) NOT NULL, password VARCHAR(255) NOT NULL );")
        cursor.execute("CREATE TABLE IF NOT EXISTS wedding_details ( id INT AUTO_INCREMENT PRIMARY KEY, theme VARCHAR(255) NOT NULL, grooms_name VARCHAR(255) NOT NULL, brides_name VARCHAR(255) NOT NULL, wedding_date DATE NOT NULL, wedding_location TEXT NOT NULL, city_name VARCHAR(255) NOT NULL, location_url VARCHAR(255) NOT NULL, email VARCHAR(255) NOT NULL );")
        cursor.execute("CREATE TABLE IF NOT EXISTS reservation ( id INT AUTO_INCREMENT PRIMARY KEY, wedding_id INT, name VARCHAR(255) NOT NULL, email VARCHAR(255) NOT NULL, phone VARCHAR(20) NOT NULL, will_attend_yes BOOLEAN, will_attend_no BOOLEAN, note TEXT );")
    
    except Exception as e:
        print(f"ERROR OCCURRED: {e}")
        flash(f"ERROR OCCURRED: {e}")
        return redirect(url_for('home'))
    
    else:
        flash("Created missing tables (if any)")
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
                        sql = "INSERT INTO users (wedding_id, name, email, password) VALUES (%s, %s, %s, %s)"
                        wedding_id = generate_random_code()
                        value = (wedding_id, userName, email, password)
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
        email = session['email']
        
        try:
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT wedding_id FROM users WHERE email = %s", (email,))
            wedding_id = cursor.fetchone()
        
        except Exception as e:
                flash(f'ERROR OCCURRED: {e}')
                return redirect(url_for('home'))
        else:
            if form.validate_on_submit():
                theme = request.form.get("theme")
                grooms_name = request.form.get("grooms_name")
                brides_name = request.form.get("brides_name")
                wedding_date = request.form.get("wedding_date")
                wedding_location = request.form.get("wedding_location")
                city_name = request.form.get("city_name")
                location_url = request.form.get("location_url")
        
                try:
                    cursor.execute("SELECT * FROM wedding_details WHERE email = %s", (email,))
                    existing_record = cursor.fetchone()

                except Exception as e:
                    flash(f'ERROR OCCURRED: {e}')
                    return redirect(url_for('home'))
                
                else:

                    if existing_record:
                        cursor.execute("UPDATE wedding_details SET theme = %s, grooms_name = %s, brides_name = %s, wedding_date = %s, wedding_location = %s, city_name = %s, location_url = %s WHERE email = %s", (theme,grooms_name, brides_name, wedding_date, wedding_location, city_name, location_url, email))
                        mysql.connection.commit()

                    else:
                        cursor.execute("INSERT INTO wedding_details (theme, grooms_name, brides_name, wedding_date, wedding_location, city_name, location_url, email) VALUES (%s,%s, %s, %s, %s, %s, %s, %s)", (theme,grooms_name, brides_name, wedding_date, wedding_location, city_name, location_url, email))
                        mysql.connection.commit()
                
                    cursor.close()
                    flash("Data Updated!")
                    return redirect(url_for('create'))
            else:
                return render_template('dashboard.html',form=form,wedding_id=wedding_id)  
    else:
        return redirect(url_for('login'))
    

@app.route("/<userinput>",methods=['GET','POST'])
@app.route("/page/<userinput>",methods=['GET','POST'])
def userpage(userinput):
        if not userinput.isdigit():
            return redirect(url_for('home'))
        
        else:
            form = ReservationForm()
            try:
                cursor = mysql.connection.cursor()
                sql = "SELECT email FROM users WHERE id = %s;"
                cursor.execute(sql, (userinput,))
                
            except Exception as e:
                flash(f'ERROR OCCURRED: {e}')
                return redirect(url_for('home'))
            
            else:
                useridfound = cursor.fetchone()

                if useridfound:
                    sql = "SELECT theme, grooms_name, brides_name, wedding_date, wedding_location, city_name, location_url FROM wedding_details WHERE email = %s"
                    value = (useridfound)
                    cursor.execute(sql,value)
                    data = cursor.fetchone()
                    try:
                        theme = data[0]
                        grooms_name = data[1]
                        brides_name = data[2]
                        wedding_date = data[3]
                        wedding_location = data[4] 
                        city_name = data[5] 
                        location_url = data[6]
                    
                    except Exception as e:
                        print(f'SOME OR ALL DATA IS MISSING: {e}')
                        return redirect(url_for('home'))
                    
                    else:
                        return render_template(f'{theme}/index.html',grooms_name=grooms_name,brides_name=brides_name,wedding_date=wedding_date,wedding_location=wedding_location,city_name=city_name,location_url=location_url,form=form)
                else:
                    print("user not found")
                    return redirect(url_for('home'))

@app.route('/reservation',methods=['POST'])
def reservation():
    form = ReservationForm()
    
    if form.is_submitted():
        wedding_id = request.form.get("wedding_id")
        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        will_attend_yes = request.form.get("will_attend_yes")
        will_attend_no = request.form.get("will_attend_no")
        note = request.form.get("note")

        try:
            cursor = mysql.connection.cursor()
        
        except Exception as e:
            flash(f'ERROR OCCURRED: {e}')
            print(f'ERROR OCCURRED: {e}')
            return redirect(url_for('home'))
            
        
        else:
            cursor.execute("INSERT INTO reservation (wedding_id, name, email, phone, will_attend_yes, will_attend_no, note) VALUES (%s, %s, %s, %s, %s, %s, %s);", (wedding_id, name, email, phone, will_attend_yes, will_attend_no, note))
            mysql.connection.commit()
            cursor.close()  
            flash("Data Submitted :)")
            return redirect(url_for('home'))
        
    else:
        flash("Alert: Form not validated")
        print("Alert: Form not validated")
        return redirect(url_for('home'))

@app.route('/create/view1')
def view():
    return render_template('template1/index.html')

if __name__ == '__main__':
    app.run(port=80,debug=True)

