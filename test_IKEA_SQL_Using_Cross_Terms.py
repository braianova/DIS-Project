
def sql_ikea_using_cross_term(connection, list_of_items,max_price,max_width,max_length,max_height):
    import numpy as np
    list_of_ints=list(np.char.mod('%d', np.arange(num_to_select)))
    list_of_items_ints = [i + j for i, j in zip(list_of_items, list_of_ints)]
    # print(list_of_items_ints )

    cursor = connection.cursor()

    #create views:
    for n in range(len(list_of_items_ints )):
        str_n="CREATE OR REPLACE VIEW "+list_of_items_ints[n] +\
            " AS  SELECT *\
            FROM ITEM \
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


    str_where_price='WHERE '+ list_of_items_ints[0]+'.PRICE'
    for n in  range(1,len(list_of_items_ints )):
        str_where_price=str_where_price+' + '+list_of_items_ints[n]+'.PRICE'  
    str_where_price=str_where_price+' <='+str(max_price)  

    str_where_width='AND '+ list_of_items_ints[0]+'.WIDTH'
    for n in  range(1,len(list_of_items_ints )):
        str_where_width=str_where_width+' + '+list_of_items_ints[n]+'.WIDTH'  
    str_where_width=str_where_width+' <='+str(max_width)  

    str_where_length='AND '+ list_of_items_ints[0]+'.LENGTH'
    for n in  range(1,len(list_of_items_ints )):
        str_where_length=str_where_length+' + '+list_of_items_ints[n]+'.LENGTH'  
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


#create connection to database (here it is assumed that the databse exists):
import psycopg2
from psycopg2 import OperationalError

def create_connection(db_name,db_user,db_password,db_host,db_port):
    connection=None
    try:
        connection=psycopg2.connect(
            database=db_name,
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port,
        )
        print("Connection to PostgresQL DB successful")
    except OperationalError as e:
        print(f"The error '{e}' occurred")
    return connection

#create connection to database (here it is assumed that the databse exists):

db_host="localhost"
# db_name="postgres" #"DIS_IKEA"
db_name="dis_ikea" #"DIS_IKEA"
db_user="postgres"
db_password="6mikael6"
db_port=5433

connection=create_connection(db_name,db_user,db_password,db_host,db_port)


#generate  user input data:
import random
group_of_items=['Sink','Mirror','Drawer','Cabinet','Bed','Wardrobe'] #list of items
num_to_select=3
list_of_items=random.choices(group_of_items,k=num_to_select)
list_of_items=['Bed','Bed','Bed']
max_price=10000
max_width=2000
max_length=2000
max_height=2000   

#do the "Ikea" query using cross terms (which is a transparent, by likely not a very efficient method):
list_of_solutions=sql_ikea_using_cross_term(connection, list_of_items,max_price,max_width,max_length,max_height)
list_of_solutions=list(set(list_of_solutions)) # list of distinct solutions
print(list_of_solutions)
 