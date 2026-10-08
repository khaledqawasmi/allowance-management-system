import psycopg2
import os

def create_connection():
    connection = psycopg2.connect(
        host = "localhost",
        database = "allowance_db",
        user = "postgres",
        password = os.getenv("DB_PASSWORD"),
        port = "5432"
    )
    return connection
try:
    connection = create_connection()
    print("Dabase connection successfuly.")
    connection.close()
except:
    print("Database connection failed.")
    print("error")