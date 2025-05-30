import mysql.connector

def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host='localhost', 
            user='root', 
            password='',  
            database='fenamaz_ecommerce_db'
        )
        if conn.is_connected():
            print('Connected to MySQL database')
            return conn
    except mysql.connector.Error as e:
        print(f"Error: {e}")
        return None


