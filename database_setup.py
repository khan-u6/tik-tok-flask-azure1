import sqlite3

# Function to create tables in the database
def init_db():
    conn = sqlite3.connect('video_sharing_platform.db')
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT NOT NULL UNIQUE,
                        password TEXT NOT NULL)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS videos (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT NOT NULL,
                        description TEXT NOT NULL,
                        video_path TEXT NOT NULL,
                        views INTEGER DEFAULT 0,
                        likes INTEGER DEFAULT 0,
                        shares INTEGER DEFAULT 0)''')

    conn.commit()
    conn.close()
    print("Database initialized successfully.")

# Initialize the database
init_db()
