from flask import Flask, render_template, request, redirect, url_for, flash
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
import os
import mongomock

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Set a secret key for message flashing

# MongoDB setup
if os.getenv("TESTING"):
    app.config["MONGO_CONN"] = mongomock.MongoClient()
else:
    URI = "mongodb://mongodb:27017/"
    app.config["MONGO_CONN"] = MongoClient(URI)

connection = app.config["MONGO_CONN"]
db = connection["edu-web"]
users = db.users

@app.route('/', methods=['GET', 'POST'])
def index():
    print("Received request for index route")
    if request.method == 'POST':
        if 'login' in request.form:
            return login()
        elif 'register' in request.form:
            return register()
    return render_template('index.html')

@app.route("/login", methods=["POST"])
def login():
    print("Processing login")
    username = request.form['username']
    password = request.form['password']
    user = users.find_one({'username': username})

    if user and check_password_hash(user['password'], password):
        flash('Logged in successfully!', 'success')
    else:
        flash('Invalid username or password', 'error')
    return redirect(url_for('index'))  # Redirect back to index after login attempt

@app.route("/register", methods=["POST"])
def register():
    print("Processing registration")
    username = request.form['username']
    password = generate_password_hash(request.form['password'])

    if users.find_one({'username': username}):
        flash('Username already exists', 'error')
    else:
        users.insert_one({'username': username, 'password': password})
        flash('Account created successfully!', 'success')
    return redirect(url_for('index'))  # Redirect back to index after registration attempt

@app.before_first_request
def init_db():
    print("Initializing database")
    print("MongoDB URI:", connection)
    print("MongoDB name:", db.name)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)





