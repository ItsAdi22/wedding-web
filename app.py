from flask import Flask, render_template,redirect ,url_for, request, flash, session
from flask_mysqldb import MySQL
from forms import SignupForm,LoginForm,WeddingDetailsForm,ReservationForm,CoupleImageForm,DeleteCoupleImage,AdminLoginForm,AdminSignupForm
from dotenv import load_dotenv
import os
import random
import datetime
from pytz import timezone 

load_dotenv()
app = Flask(__name__)
mysql = MySQL(app)

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['DOMAIN'] = os.getenv('DOMAIN')

app.config["MYSQL_HOST"] = os.getenv('MYSQL_HOST')
app.config["MYSQL_DB"] = os.getenv('MYSQL_DB')
app.config["MYSQL_USER"] = os.getenv('MYSQL_USER')
app.config["MYSQL_PASSWORD"] = os.getenv('MYSQL_PASSWORD')


#generate wedding id
def generate_random_code():
    return str(random.randint(10000, 99999))


# Function to store the uploaded images based on wedding_id
def store_images(wedding_id, groom_image, bride_image):
    # Create a directory if it doesn't exist
    upload_dir = os.path.join(app.config['UPLOAD_FOLDER'], str(wedding_id[0]))
    os.makedirs(upload_dir, exist_ok=True)

    # rename the images
    if groom_image or bride_image is not None:
        groom_filename = f"groom_image.{groom_image.filename.split('.')[-1]}"
        bride_filename = f"bride_image.{bride_image.filename.split('.')[-1]}"
        # Save groom image
        groom_image.save(os.path.join(upload_dir, groom_filename))
        # Save bride image
        bride_image.save(os.path.join(upload_dir, bride_filename))
    else:
        print("blank data submitted")
    
    flash('Images uploaded successfully')

# To get the month of wedding in text format
months_dict = {
    "01": "January",
    "02": "February",
    "03": "March",
    "04": "April",
    "05": "May",
    "06": "June",
    "07": "July",
    "08": "August",
    "09": "September",
    "10": "October",
    "11": "November",
    "12": "December"
}

@app.route('/tables')
def createtables():
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS users ( id INTEGER PRIMARY KEY AUTO_INCREMENT, wedding_id INTEGER, name VARCHAR(255) NOT NULL, email VARCHAR(255) NOT NULL, password VARCHAR(255) NOT NULL );")
        cursor.execute("CREATE TABLE IF NOT EXISTS wedding_details ( id INT AUTO_INCREMENT PRIMARY KEY, theme VARCHAR(255) NOT NULL, grooms_name VARCHAR(255) NOT NULL, brides_name VARCHAR(255) NOT NULL, wedding_date DATE NOT NULL, wedding_location TEXT NOT NULL, city_name VARCHAR(255) NOT NULL, location_url VARCHAR(255) NOT NULL, email VARCHAR(255) NOT NULL );")
        cursor.execute("CREATE TABLE IF NOT EXISTS reservation ( id INT AUTO_INCREMENT PRIMARY KEY, wedding_id INT, name VARCHAR(255) NOT NULL, email VARCHAR(255) NOT NULL, phone VARCHAR(20) NOT NULL, will_attend BOOLEAN, guests VARCHAR(20) NOT NULL, note TEXT );")
        cursor.execute("CREATE TABLE IF NOT EXISTS admin ( id INT AUTO_INCREMENT PRIMARY KEY, email VARCHAR(255), password VARCHAR(255) );")
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
            return render_template('login/signup.html', form=form)


@app.route('/signin',methods=['POST','GET'])
@app.route('/login',methods=['POST','GET'])
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
@app.route('/dashboard',methods=['POST','GET'])
def create():
    if 'email' in session:
        form = WeddingDetailsForm()
        form2 = CoupleImageForm()
        form3 = DeleteCoupleImage()
        email = session['email']
        domain = app.config['DOMAIN']
        
        try:
            cursor = mysql.connection.cursor()
            
            cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
            userid = cursor.fetchone()
            
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
            
            #process groom and bride images
            elif form2.validate_on_submit():
                groom_image = form2.groom.data or None
                bride_image = form2.bride.data or None
                store_images(wedding_id, groom_image, bride_image)
                
                
                folder_path = os.path.join(app.config['UPLOAD_FOLDER'], str(wedding_id[0]))
                print(f"folder path: {folder_path}")
                # Create the directory if it doesn't already exist

                images = os.listdir(folder_path)

                # if there are more than two images in folder
                if (len(images) > 2):
                    for x in os.listdir(folder_path):
                        file_path = os.path.join(folder_path,x)
                        if os.path.isfile(file_path):
                            os.remove(file_path)
                    flash("You cannot upload more than two images!")
                
                return redirect(url_for('create'))
            
            elif form3.validate_on_submit():
                folder_path = os.path.join(app.config['UPLOAD_FOLDER'], str(wedding_id[0]))
                images = os.listdir(folder_path)
                
                for x in os.listdir(folder_path):
                        file_path = os.path.join(folder_path,x)
                        if os.path.isfile(file_path):
                            os.remove(file_path)
                            if(len(images) == 1):
                                flash("Images Deleted")
                                print('Images Deleted')
                        
                return redirect(url_for('create'))
            else:
                try:
                    cursor = mysql.connection.cursor()
                    sql = ('SELECT theme, grooms_name, brides_name, wedding_date, wedding_location, city_name, location_url, email FROM wedding_details WHERE email = %s')
                    values = (email,)
                    cursor.execute(sql,values)
                
                except Exception as e:
                    flash(f'ERROR OCCURRED: {e}')
                    return redirect(url_for('home'))
                
                else:
                    
                    wedding_details = cursor.fetchone()

                    if wedding_details:
                        theme = wedding_details[0] 
                        grooms_name = wedding_details[1]
                        brides_name = wedding_details[2]
                        wedding_date = wedding_details[3]
                        wedding_location = wedding_details[4]
                        city_name = wedding_details[5]
                        location_url = wedding_details[6]
                    
                    else:
                        theme = "" 
                        grooms_name = ""
                        brides_name = ""
                        wedding_date = ""
                        wedding_location = ""
                        city_name = ""
                        location_url = ""
                        print('No wedding details found for the provided email.')



                    folder_path = os.path.join(app.config['UPLOAD_FOLDER'], str(wedding_id[0]))

                    try:    
                        if not os.path.exists(folder_path):
                            os.makedirs(folder_path)
                            print(f"Directory created at {folder_path}")
                        else:
                            print(f"Directory already exists at {folder_path}")

                    except Exception as e:
                        print(f'ERROR OCCURRED: {e}')

                    images = os.listdir(folder_path)
                    images_count = len(images)

                    return render_template('dashboard.html',form=form,form2=form2,form3=form3,theme=theme,wedding_id=wedding_id,userid=userid[0],domain=domain,grooms_name=grooms_name,brides_name=brides_name,wedding_date=wedding_date,wedding_location=wedding_location,city_name=city_name,location_url=location_url,images_count=images_count)  
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

                useridfound = cursor.fetchone()

                #get wedding id
                sql = "SELECT wedding_id FROM users WHERE email = %s"
                cursor.execute(sql,useridfound)
                wedding_id = cursor.fetchone()
                
            except Exception as e:
                flash(f'ERROR OCCURRED: {e}')
                return redirect(url_for('home'))
            
            else:
                

                if useridfound:
                    sql = "SELECT theme, grooms_name, brides_name, wedding_date, wedding_location, city_name, location_url FROM wedding_details WHERE email = %s"
                    value = (useridfound)
                    cursor.execute(sql,value)
                    data = cursor.fetchone()
                    try:
                        if data:
                            theme = data[0]
                            grooms_name = data[1]
                            brides_name = data[2]
                            wedding_date = data[3]
                            wedding_location = data[4] 
                            city_name = data[5] 
                            location_url = data[6]
                        
                        else:
                            theme = "template1" # default theme
                            grooms_name = ""
                            brides_name = ""
                            wedding_date = ""
                            wedding_location = "" 
                            city_name = "" 
                            location_url = ""

                    
                        #calculate date
                        # Parse the date string into a datetime object
                        # Check if wedding_date is already a datetime.date object
                        if isinstance(wedding_date, datetime.date):
                            given_date = wedding_date  # No need to parse, use it directly

                        else:
                            # setting a sample date if the wedding_date data is empty
                            if (wedding_date == ""):
                                wedding_date = "2001-11-09"
                            # Parse the date string into a datetime object
                            try:
                                given_date = datetime.datetime.strptime(wedding_date, "%Y-%m-%d").date()
                            except ValueError:
                                print("Invalid date format. Please use YYYY-MM-DD format.")
                                print(given_date)
                                return redirect(url_for('home'))

                        # Proceed with the calculations if parsing was successful
                        if given_date:
                            # Specify the target time zone (replace with the appropriate one)
                            target_timezone = timezone("Asia/Kolkata")  # Example: Asia/Kolkata

                            # Convert both dates to the target time zone
                            given_date_tz = datetime.datetime.combine(given_date, datetime.time.min).astimezone(target_timezone)
                            current_date_tz = datetime.datetime.now(target_timezone)

                            difference =  given_date_tz - current_date_tz

                            # Calculate remaining time components
                            total_seconds = difference.total_seconds()
                            remaining_days = int(total_seconds // (24 * 60 * 60))
                            remaining_hours = int((total_seconds % (24 * 60 * 60)) // 3600)
                            remaining_minutes = int((total_seconds % 3600) // 60)
                            remaining_seconds = int(total_seconds % 60)

                            # now get the groom and bride images:
                            folder_path = os.path.join(app.config['UPLOAD_FOLDER'], str(wedding_id[0]))
                            
                            images = os.listdir(folder_path)

                            print(f'images len---> {len(images)}')
                            
                            
                            if (len(images) == 2):
                                groom_image = images[1] 
                                bride_image = images[0] 

                            else:
                                groom_image = False
                                bride_image = False
                            print(f'groom img ====> {groom_image}')
                            print(f'groom img ====> {bride_image}')
                    except Exception as e:
                        print(f'SOME OR ALL DATA IS MISSING: {e}')
                        return redirect(url_for('home'))
                    
                    else:
                        
                        #convert wedding date in string format
                        wedding_date = (f'{str(wedding_date)[8:10]}th {months_dict[str(wedding_date)[5:7]]} {str(wedding_date)[0:4]}')

                        return render_template(f'{theme}/index.html',grooms_name=grooms_name,brides_name=brides_name,wedding_date=wedding_date,wedding_location=wedding_location,city_name=city_name,location_url=location_url,form=form,days=remaining_days,hours=remaining_hours,minutes=remaining_minutes,seconds=remaining_seconds,groom_image=groom_image,bride_image=bride_image,images=images,wedding_id=str(wedding_id[0]))
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
        will_attend = request.form.get("will_attend")
        guests = request.form.get("guests")
        note = request.form.get("note")

        try:
            cursor = mysql.connection.cursor()
        
        except Exception as e:
            flash(f'ERROR OCCURRED: {e}')
            print(f'ERROR OCCURRED: {e}')
            return redirect(url_for('home'))
            
        
        else:
            cursor.execute("INSERT INTO reservation (wedding_id, name, email, phone, will_attend, guests,note) VALUES (%s,%s, %s, %s, %s, %s, %s);", (wedding_id, name, email, phone, will_attend, guests, note))
            mysql.connection.commit()

            sql = "SELECT id FROM users WHERE wedding_id = %s"
            value = (wedding_id,)
            cursor.execute(sql,value)
            userid = cursor.fetchone()
            if userid:
                userinput = userid[0]
            else:
                flash("Invalid wedding Id")
                return redirect(url_for('home'))
            cursor.close()  
            flash("Data Submitted :)")
            return redirect(url_for('userpage',userinput = userinput))
        
    else:
        flash("Alert: Form not validated")
        print("Alert: Form not validated")
        return redirect(url_for('home'))

@app.route('/entries')
def entries():
    if 'email' in session:
        email = session['email']
        try:
            cursor = mysql.connection.cursor()
        
        except Exception as e:
            flash(f'ERROR OCCURRED: {e}')
            return redirect(url_for('home'))
        else:
            sql = "SELECT wedding_id FROM users WHERE email = %s;"
            value = (email,)
            cursor.execute(sql,value)
            wedding_id = cursor.fetchone()

            sql = "SELECT name, email, phone, will_attend, guests, note FROM reservation WHERE wedding_id = %s;"
            value=(wedding_id,)
            cursor.execute(sql,value)
            attendies = cursor.fetchall()
            
            sql = 'SELECT sum(guests) FROM reservation WHERE wedding_id = %s;'
            value=(wedding_id,)
            cursor.execute(sql,value)
            total_guests = cursor.fetchone()
        return render_template('entries.html',attendies=attendies,total_guests=total_guests)
    
# admin panel
@app.route('/admin',methods=['POST','GET'])
def admin():
    if 'admin' in session:
        return render_template('admin/index.html')
    
    else:
        try:
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT * FROM admin")
            admin_exists = cursor.fetchall()
        
        except Exception as e:
            flash(f"ERROR OCCURRED: {e}")
            return redirect(url_for('home'))

        else:
            if admin_exists:
                return render_template('admin/login.html')
            
            else:
                return render_template('admin/signup.html')

@app.route('/admin/login',method=["POST","GET"])
def adminlogin():
    form = AdminLoginForm()
    form2 = AdminSignupForm()
    if 'admin' in session:
        return redirect(url_for('admin'))
    
    else:
        pass

if __name__ == '__main__':
    app.run(host=os.getenv('DOMAIN'),port=80,debug=True)

