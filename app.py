import os
import psycopg2
import psycopg2.extras
from flask import Flask, render_template, session, request, url_for, redirect, Blueprint, flash, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import re
import numpy as np
import random

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


solutions_dict = {}

def get_db_connection():
    conn = psycopg2.connect(host = 'localhost',
                            database = 'ikea_db',
                            user = 'postgres',
                            password = 'B1gR3dD0g!')
    return conn




# Decorater: tells us which functions should  
# run when someone visits a specified page
@app.route("/", methods=['GET','POST']) # / is just the main home page
def index():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    # Check if user is logged in
    if 'loggedin' in session:
        
        # User is loggedin show them the home page
        uid = session['id']
        cursor.execute('SELECT * FROM rooms WHERE uid = %s', (uid,))
        rooms = cursor.fetchall()
        
        
        if request.method == 'POST' and 'room_budget' in request.form and 'room_width' in request.form and 'room_depth' in request.form and 'room_height' in request.form:
            
            room_type = 'Bedroom'
            room_budget = int(float(request.form['room_budget']))
            room_width = int(float(request.form['room_width']))
            room_depth = int(float(request.form['room_depth']))
            room_height = int(float(request.form['room_height']))
            
            cursor.execute('INSERT INTO rooms (uid, room_type, room_budget, room_width, room_depth, room_height)'
                        'VALUES (%s, %s, %s, %s, %s, %s)',
                        (uid, room_type, room_budget, room_width, room_depth, room_height))
            conn.commit()
        
        for room in rooms:
            room_id = room[1]
            room_type = room[2]
            room_budget = room[3]
            room_width = room[4]
            room_depth = room[5]
            room_height = room[6]

            list_of_solutions = []
            if room_type == 'Bedroom':
                list_of_items = ['Bed', 'Drawer', 'Wardrobe', 'Mirror']
                list_of_solutions = list(set(sql_ikea_using_cross_term(conn, list_of_items, room_budget, room_width, room_depth, room_height)))[5000:5005]
                print(len(list_of_solutions))
                if room_id in solutions_dict:
                    continue
                else:
                    solutions_dict[room_id] = list_of_solutions


        cursor.close()
        conn.close()

        return render_template('index.html', username=session['username'], rooms=rooms, solutions_dict = solutions_dict)
    
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

                                      
@app.route('/about')                
def about():
    message = ''' Welcome to the Bedroom Interior Designer! This website uses IKEA products to furnish your dream bedroom. For those who don't know where to start where it comes to designing, Bedroom Interior Designer is here to help. We generate a variety of combinations for bed, wardrobe, dresser, and mirror options for your budget and room size. Submit your budget and dimensions to start!  '''
    return render_template('about.html', message = message)
    
                    
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
                    
                    
def sql_ikea_using_cross_term(connection, list_of_items, max_price, max_width, max_length, max_height):
    num_to_select = len(list_of_items)
    list_of_ints=list(np.char.mod('%d', np.arange(num_to_select)))
    list_of_items_ints = [i + j for i, j in zip(list_of_items, list_of_ints)]
    # print(list_of_items_ints )

    cursor = connection.cursor()

    #create views:
    for n in range(len(list_of_items_ints )):
        str_n="CREATE OR REPLACE VIEW "+list_of_items_ints[n] +\
            " AS  SELECT *\
            FROM ikea_items \
            WHERE TYPE = '"+ list_of_items[n]+"';"
        sql_n=str_n
        cursor.execute(sql_n)
        
    #create SQL query:
    str_select='SELECT '+list_of_items_ints[0]+'.name'
    for n in  range(1,len(list_of_items_ints )):
        str_select=str_select+', '+list_of_items_ints[n]+'.name'  

    str_from='FROM '+ list_of_items_ints[0]
    for n in range(1,len(list_of_items_ints)):
        str_from=str_from+' CROSS JOIN '+list_of_items_ints[n]


    str_where_price='WHERE '+ list_of_items_ints[0]+'.price'
    for n in  range(1,len(list_of_items_ints )):
        str_where_price=str_where_price+' + '+list_of_items_ints[n]+'.price'  
    str_where_price=str_where_price+' <='+str(max_price)  

    str_where_width='AND '+ list_of_items_ints[0]+'.WIDTH'
    for n in  range(1,len(list_of_items_ints )):
        str_where_width=str_where_width+' + '+list_of_items_ints[n]+'.WIDTH'  
    str_where_width=str_where_width+' <='+str(max_width)  

    str_where_length='AND '+ list_of_items_ints[0]+'.depth'
    for n in  range(1,len(list_of_items_ints )):
        str_where_length=str_where_length+' + '+list_of_items_ints[n]+'.depth'  
    str_where_length=str_where_length+' <='+str(max_length) 

    str_where_height='AND '+ list_of_items_ints[0]+'.HEIGHT'
    for n in  range(1,len(list_of_items_ints )):
        str_where_height=str_where_height+' + '+list_of_items_ints[n]+'.HEIGHT'  
    str_where_height=str_where_height+' <='+str(max_height) 

    sql_ikea=str_select +' \n ' + str_from + ' \n ' + str_where_price +' \n ' \
        +str_where_width+' \n ' + str_where_length+' \n ' + str_where_height+";"
    # print(sql_ikea)

    cursor.execute(sql_ikea)
    list_of_solutions=[]
    for i in cursor.fetchall():
        list_of_solutions.append(i)
        # print(i)

    #drop views:
    for n in range(len(list_of_items_ints )):
        str_n="DROP VIEW "+list_of_items_ints[n] +";"
        sql_n=str_n
        cursor.execute(sql_n)

    
    return list_of_solutions

                    
                 
                    
                    
                    
# Are you runnning it as a program, or 
# are you using it as a module
if __name__ == "__main__":
    # app.run runs the web application
    app.run(host="0.0.0.0", debug=True, threaded=False) 

# app.run never returns, so don't define functions
# after this (the def lines will never be reached)
