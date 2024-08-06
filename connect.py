import mysql.connector

# Replace with your MySQL database credentials
db_config = {
    'user': 'root',
    'password': '',
    'host': 'localhost',
    'database': 'face_detection'
}

connection = mysql.connector.connect(**db_config)
mycursor = connection.cursor()
print(db_config)
