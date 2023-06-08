import os
import psycopg2
import psycopg2.extras
from flask import Flask, render_template, session, request, url_for, redirect, Blueprint, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import re

# init SQLAlchemy so we can use it later in our models
db = SQLAlchemy()

app = Flask(__name__)

app.config['SECRET_KEY'] = '1234'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://braianova:victoria@localhost/ikea_db'

db.init_app(app)

# blueprint for auth routes in our app
auth_blueprint = Blueprint('auth', __name__)
app.register_blueprint(auth_blueprint)

# blueprint for non-auth parts of app
main_blueprint = Blueprint('main', __name__)
app.register_blueprint(main_blueprint)

def get_db_connection():
    conn = psycopg2.connect(host = 'localhost',
                            database = 'ikea_db',
                            user = 'postgres',
                            password = 'B1gR3dD0g!')
    return conn




# Decorater: tells us which functions should  
# run when someone visits a specified page
@app.route("/") # / is just the main home page
def index():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    # Check if user is logged in
    if 'loggedin' in session:
        # User is loggedin show them the home page
        uid = session['id']
        cursor.execute('SELECT * FROM rooms WHERE uid = %s', (uid,))
        rooms = cursor.fetchall()
        return render_template('index.html', username=session['username'], rooms=rooms)
    
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

@app.route('/login', methods=['GET','POST'])
def login():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        print(password)
 
        # Check if account exists using MySQL
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        
        # Fetch one record and return result
        account = cursor.fetchone()
 
        if account:
            password_rs = account['password']
            print(password_rs)
            # If account exists in users table in out database
            if check_password_hash(password_rs, password):
                # Create session data, we can access this data in other routes
                session['loggedin'] = True
                session['id'] = account['id']
                session['username'] = account['username']
                # Redirect to home page
                return redirect(url_for('index'))
            else:
                # Account doesnt exist or username/password incorrect
                flash('Incorrect password')
                
        else:
            # Account doesnt exist or username/password incorrect
            flash("User doesn't exist. Please register below.")
 
    return render_template('login.html')
  
                    
                    
                    
                    
                    
                    
                    

@app.route('/register', methods=['GET', 'POST'])
def register():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
 
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        fullname = request.form['fullname']
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
    
        _hashed_password = generate_password_hash(password)
 
        #Check if account exists using MySQL
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        account = cursor.fetchone()
        print(account)
        # If account exists show error and validation checks
        if account:
            flash('Account already exists!')
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            flash('Invalid email address!')
        elif not re.match(r'[A-Za-z0-9]+', username):
            flash('Username must contain only characters and numbers!')
        elif not username or not password or not email:
            flash('Please fill out the form!')
        else:
            # Account doesnt exists and the form data is valid, now insert new account into users table
            cursor.execute("INSERT INTO users (fullname, username, password, email) VALUES (%s,%s,%s,%s)", (fullname, username, _hashed_password, email))
            conn.commit()
            flash('You have successfully registered!')
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        flash('Please fill out the form!')
    # Show registration form with message (if any)
    return render_template('register.html')

                    
                    
                    
                    
                    
                    
                    
                    
@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   # Redirect to login page
   return redirect(url_for('login'))

                    
                    
                    
@app.route('/profile')
def profile(): 
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Check if user is loggedin
    if 'loggedin' in session:
        cursor.execute('SELECT * FROM users WHERE id = %s', [session['id']])
        account = cursor.fetchone()
        # Show the profile page with account info
        return render_template('profile.html', account=account)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))                   
                    
                    
                    
                    
                    
                    
                    
                    
@app.route('/create', methods=('GET', 'POST'))
def create():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if request.method == 'POST':
        room_type = request.form['room_type']
        room_budget = int(float(request.form['room_budget']))
        room_width = int(float(request.form['room_width']))
        room_depth = int(float(request.form['room_depth']))
        room_height = int(float(request.form['room_height']))
        uid = session['id']
        cursor.execute('INSERT INTO rooms (uid, room_type, room_budget, room_width, room_depth, room_height)'
                    'VALUES (%s, %s, %s, %s, %s, %s)',
                    (uid, room_type, room_budget, room_width, room_depth, room_height))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('index'))
    return render_template('create.html')

                    
                    
                    
                    
                    
                    
                    
# Are you runnning it as a program, or 
# are you using it as a module
if __name__ == "__main__":
    # app.run runs the web application
    app.run(host="0.0.0.0", debug=True, threaded=False) 

# app.run never returns, so don't define functions
# after this (the def lines will never be reached)
