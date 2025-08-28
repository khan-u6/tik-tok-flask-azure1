from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os
import sqlite3
import bcrypt
import jwt
import datetime

app = Flask(__name__)

# Database setup
DATABASE = 'video_sharing_platform.db'

# Secret key for JWT encoding and decoding
app.config['SECRET_KEY'] = 'your_secret_key'


# Function to get a database connection
def get_db():
    conn = sqlite3.connect(DATABASE)
    return conn


# Create the tables if they don't exist
def init_db():
    conn = get_db()
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


# Initialize the database
init_db()


# User registration endpoint
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data['username']
    password = data['password']

    # Check if user already exists
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()

    if user:
        return jsonify({"message": "User already exists"}), 400

    # Hash the password
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    # Insert new user into the database
    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
    conn.commit()
    conn.close()

    return jsonify({"message": "User registered successfully"}), 201


# User login endpoint
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']

    # Check if user exists
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()

    if not user:
        return jsonify({"message": "User not found"}), 400

    # Check if password matches
    if not bcrypt.checkpw(password.encode('utf-8'), user[2].encode('utf-8')):
        return jsonify({"message": "Invalid credentials"}), 400

    # Create JWT token
    token = jwt.encode({'user_id': user[0], 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)},
                       app.config['SECRET_KEY'], algorithm='HS256')

    return jsonify({"token": token}), 200


# Video upload endpoint
@app.route('/upload', methods=['POST'])
def upload_video():
    title = request.form['title']
    description = request.form['description']
    video_file = request.files['video']

    # Save video file to server
    filename = secure_filename(video_file.filename)
    video_path = os.path.join('uploads', filename)
    video_file.save(video_path)

    # Insert video data into the database
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO videos (title, description, video_path) VALUES (?, ?, ?)",
                   (title, description, video_path))
    conn.commit()
    conn.close()

    return jsonify({"message": "Video uploaded successfully"}), 201


# Get all videos
@app.route('/videos', methods=['GET'])
def get_videos():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM videos")
    videos = cursor.fetchall()
    conn.close()

    video_list = []
    for video in videos:
        video_list.append({
            'id': video[0],
            'title': video[1],
            'description': video[2],
            'video_path': video[3],
            'views': video[4],
            'likes': video[5],
            'shares': video[6]
        })

    return jsonify(video_list), 200


if __name__ == '__main__':
    if not os.path.exists('uploads'):
        os.makedirs('uploads')  # Create the uploads folder if it doesn't exist
    app.run(debug=True, host='0.0.0.0', port=5000)
