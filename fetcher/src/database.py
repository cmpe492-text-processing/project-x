import psycopg2
from psycopg2 import OperationalError
import os
from dotenv import load_dotenv
def create_connection():
    conn = None
    try:
        conn = psycopg2.connect(
            host=os.getenv('host'),
            port=os.getenv('port'),
            dbname=os.getenv('dbname'),
            user=os.getenv('user'),
            password=os.getenv('db-password')
        )
        print("Connection to PostgreSQL DB successful")
    except OperationalError as e:
        print(f"The error '{e}' occurred")
    return conn


def execute_query(connection, query):
    connection.autocommit = True
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        print("Query executed successfully")
    except OperationalError as e:
        print(f"The error '{e}' occurred")


# Example usage
if __name__ == "__main__":
    load_dotenv('../.env')

    connection = create_connection()

    if connection is not None:
        connection.close()
