import mysql.connector

def get_db_connection():
    # Replace with your MySQL database credentials
    db_config = {
        'user': 'root',
        'password': '',
        'host': 'localhost',
        'database': 'face_detection'
    }

    try:
        connection = mysql.connector.connect(**db_config)
        return connection
    except mysql.connector.Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None
