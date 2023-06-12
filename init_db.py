import os
import psycopg2

conn = psycopg2.connect(
		host ="localhost",
		database = "ikea_db",
		user='postgres',
		password='B1gR3dD0g!')

# Open a cursor to perform database operations
cur = conn.cursor()
cur.execute('DROP TABLE IF EXISTS ikea_items;')
cur.execute('''CREATE TABLE ikea_items(name varchar NOT NULL, 
                                       iid varchar (10) PRIMARY KEY, 
                                       type varchar NOT NULL,
                                       room varchar NOT NULL,
                                       price integer NOT NULL,
                                       width integer,
                                       depth integer,
                                       height integer);''')

with open('IKEA_Items.csv', 'r') as f:
    # Notice that we don't need the csv module.
    next(f) # Skip the header row.
    cur.copy_from(f, 'ikea_items', sep=',')
    
cur.execute('DROP TABLE IF EXISTS rooms;')
cur.execute('''CREATE TABLE rooms(uid integer,
                                  rid SERIAL PRIMARY KEY,
                                  room_type varchar NOT NULL, 
                                  room_budget decimal,
                                  room_width decimal,
                                  room_depth decimal,
                                  room_height decimal);''')

cur.execute('DROP TABLE IF EXISTS users;')
cur.execute('''CREATE TABLE users(id SERIAL PRIMARY KEY, 
                                  fullname varchar NOT NULL, 
                                  username varchar NOT NULL,
                                  password varchar NOT NULL,
                                  email varchar NOT NULL);''')
    
    
conn.commit()
cur.close()
conn.close()
