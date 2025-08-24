from flask import Flask
from flask import render_template
from flask import flash
from flask import request , redirect, url_for ,session
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector

app = Flask(__name__)
# Debug setting set to true 
app.secret_key = "Success"
app.debug = True

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",         # leave empty if you're using default XAMPP config
    database="institute" # the name of your database
)

cursor = db.cursor()


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/courses')
def courses():
    return render_template('courses.html')

@app.route('/details')
def details():
    return render_template('details.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        data = request.form
        email = data.get('email')
        password = data.get('password')

        sql = "SELECT * FROM users WHERE email = %s"
        cursor.execute(sql,(email,))
        user = cursor.fetchone()

        if user:
            stored_hashed_password = user[2]

            if check_password_hash(stored_hashed_password,password):
                session['user'] = user[1]
                session['is_admin'] = user[3]

                flash("Login Successful!")
                return redirect(url_for("home"))
            
            else:
                flash("Incorrect password")

        else:
            flash("No User Found")

    return render_template('login.html')

@app.route('/register', methods=['GET','POST'])
def reg():
    if request.method == 'POST':
        data = request.form
        email = data.get('email')
        passs = generate_password_hash(data.get('password'))
    
        reg = {
        "email":email,
        "password":passs
        }
        
        sql = "INSERT INTO users (email, password) VALUES (%s, %s)"
        values = (email, passs)
        cursor.execute(sql, values)
        db.commit()

        flash("Registration successful!")
        return redirect(url_for('home'))
    return render_template('register.html')

@app.route('/form', methods=['GET' , 'POST'])
def form():
    if 'user' not in session:
        flash('Login First!')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        data = request.form
        name = data.get('name')
        fname = data.get('fname')
        date = data.get('date')
        no = data.get('number')
        address = data.get('address')
        email = data.get('email')
        course = data.get('course')
        gender = data.get('gender')
        profession = data.get('profession')
        error ={}

        if len(name) < 10:
            error['name'] = "*Name must be greater than 10*"

        if len(no) != 10:
            error['number'] = "*Enter Valid 10 digit number*"

        if len(email) < 5:
            error['email'] = "*email must be greater than 5*"
            
        #if (course) != "Python Programming" or "Java Development" or "C Programming" or "Web Development" or "PHP" or "Java Script" or "C++" or "MySQL":
        #    d = "Enter Valid Course as written"
        #    error.append(d)

        if error:
            return render_template('form.html',error=error)
        
        user_info = {
            "name": name,
            "fname": fname,
            "date": date,
            "no": no,
            "address": address,
            "email": email,
            "course": course,
            "gender":gender,
            "profession":profession
        }
        sql = "INSERT INTO registrations (name, phone, email, course) VALUES (%s, %s, %s, %s)"
        values = (name, no, email, course)
        cursor.execute(sql, values)
        db.commit()
    
        flash("Registration successful!")
        return redirect(url_for('home'))
                
    return render_template('form.html',error={})

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash("Logged Out.")
    return redirect(url_for('home'))

@app.route('/admin')
def admin():
    if 'user' not in session or session.get('is_admin') != 1:
        flash("Access Denied")
        return redirect(url_for("home"))
    cursor = db.cursor()
    cursor.execute("SELECT * FROM registrations")
    user = cursor.fetchall()
    return render_template('admin.html',user=user)

@app.route('/delete/<int:user_id>')
def delete_user(user_id):
    if 'user' not in session or session.get('is_admin') != 1:
        flash('Access Denied')
        return redirect(url_for('home'))     

    cursor = db.cursor()
    cursor.execute('DELETE FROM registrations WHERE id = %s', (user_id,))
    db.commit()
    cursor.close()
    flash("Delete Successful!")       
    return redirect(url_for('admin'))

@app.route('/edit/<int:user_id>')
def edit_user(user_id):
    if 'user' not in session or session.get('is_admin') != 1:
        flash('Access Denied')
        return redirect(url_for('home'))     

    cursor = db.cursor()
    cursor.execute('SELECT * FROM registrations WHERE id = %s', (user_id,))
    user = cursor.fetchone()
    cursor.close()

    if not user:
        flash('User not found')
        return redirect(url_for('admin'))
    return render_template('edit.html', user=user)

@app.route('/update/<int:user_id>',methods=['POST'])
def update_user(user_id):
    if 'user' not in session or session.get('is_admin') != 1:
        flash('Access Denied')
        return redirect(url_for('home'))
    
    data = request.form
    name = data.get('name')
    phone = data.get('phone')
    email = data.get('email')
    course = data.get('course')

    cursor = db.cursor()
    cursor.execute('''UPDATE registrations
                   SET name = %s, phone = %s, email = %s, course = %s
                   WHERE id = %s
                   ''',(name,phone,email,course,user_id))
    db.commit()
    cursor.close()
    flash('Edit Successful!')
    return redirect(url_for('admin'))
