import sqlite3


def connect_db(db_path="user_database.db"):
    """Connect to the SQLite database."""
    try:
        conn = sqlite3.connect(db_path)
        print("Connected to the database successfully!")
        return conn
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
        return None


def close_db(conn):
    """Close the database connection."""
    if conn:
        conn.close()
        print("Database connection closed.")
