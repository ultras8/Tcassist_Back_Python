import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            port=os.getenv("DB_PORT")
        )
        print("✅ Connection Successful!")
        return conn
    except Exception as e:
        print(f"❌ Error connecting to database: {e}")
        return None

if __name__ == "__main__":
    get_connection()