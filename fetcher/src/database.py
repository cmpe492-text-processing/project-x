import psycopg2
from psycopg2 import OperationalError
import os
from dotenv import load_dotenv
import json

def create_connection():
    try:
        # Connect to the database using DATABASE_URL environment variable
        connection = psycopg2.connect(os.getenv('DATABASE_URL'), sslmode='require')
        print("Connection to PostgreSQL DB successful")
        return connection
    except OperationalError as e:
        print(f"The error '{e}' occurred")
        return None

class DatabaseManager:
    def __init__(self):
        load_dotenv('../.env')
        self.connection = create_connection()

    def execute_query(self, query):
        if self.connection is not None:
            self.connection.autocommit = True
            cursor = self.connection.cursor()
            try:
                cursor.execute(query)
                print("Query executed successfully")
            except OperationalError as e:
                print(f"The error '{e}' occurred")
            finally:
                cursor.close()

    def insert_corpuses(self, corpuses):
        if self.connection is not None:
            cursor = self.connection.cursor()
            query = """
            INSERT INTO corpuses (platform, entry_id, data)
            VALUES (%s, %s, %s::jsonb)
            ON CONFLICT (platform, entry_id) DO NOTHING;
            """
            for corpus in corpuses:
                json_data = json.dumps(corpus, indent=0)
                values = (corpus['platform'], corpus['id'], json_data)

                try:
                    cursor.execute(query, values)
                    print("Query executed successfully")
                except OperationalError as e:
                    print(f"The error '{e}' occurred")

            self.connection.commit()
            cursor.close()

    def insert_posts(self, posts):
        if self.connection is not None:
            cursor = self.connection.cursor()
            query = """
            INSERT INTO posts (id, author_id, created_utc, name, permalink, score, selftext, subreddit, title, upvote_ratio)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING;
            """
            for post in posts:
                values = (
                post.id, post.author_id, post.created_utc, post.name, post.permalink, post.score, post.selftext,
                post.subreddit, post.title, post.upvote_ratio)

                try:
                    cursor.execute(query, values)
                    print("Query executed successfully")
                except OperationalError as e:
                    print(f"The error '{e}' occurred")

            self.connection.commit()
            cursor.close()

    def close_connection(self):
        if self.connection is not None:
            self.connection.close()
            print("Database connection closed.")
