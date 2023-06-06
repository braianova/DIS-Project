import os
import psycopg2
from flask import Flask, render_template, request, url_for, redirect

app = Flask(__name__)

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
    cur = conn.cursor()
#     cur.execute('SELECT * FROM ikea_items;')
#     items = cur.fetchall()
    cur.execute('SELECT * FROM rooms;')
    rooms = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("index.html", rooms = rooms)

@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        room_type = request.form['room_type']
        room_budget = int(float(request.form['room_budget']))
        room_width = int(float(request.form['room_width']))
        room_depth = int(float(request.form['room_depth']))
        room_height = int(float(request.form['room_height']))

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('INSERT INTO rooms (room_type, room_budget, room_width, room_depth, room_height)'
                    'VALUES (%s, %s, %s, %s, %s)',
                    (room_type, room_budget, room_width, room_depth, room_height))
        conn.commit()
        cur.close()
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
