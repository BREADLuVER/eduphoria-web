from flask import Flask, render_template, request, redirect, url_for, flash
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo.errors import PyMongoError
import os
from flask import session
import mongomock

app = Flask(__name__)
app.secret_key = 'your_secret_key' 

# if os.getenv("TESTING") == True:
#     app.config["MONGO_CONN"] = mongomock.MongoClient()
# else:
#     URI = "mongodb://mongodb:27017/"
#     app.config["MONGO_CONN"] = MongoClient(URI)

URI = os.getenv('MONGO_URI', 'default-mongodb-uri')
app.config["MONGO_CONN"] = MongoClient(URI)
connection = app.config["MONGO_CONN"]
db = connection["edu-web"]
users = db.users

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'login' in request.form:
            return login()
        elif 'register' in request.form:
            return register()
    return render_template('index.html')

@app.route("/login", methods=["POST"])
def login():
    email = request.form['email']
    password = request.form['password']
    user = users.find_one({'email': email})

    if user and check_password_hash(user['password'], password):
        flash('Logged in successfully!', 'success')
        session['logged_in'] = True  # Set session variable
    else:
        flash('Invalid email or password', 'error')
    return redirect(url_for('index'))

@app.route("/register", methods=["POST"])
def register():
    email = request.form['email']
    password = generate_password_hash(request.form['password'])

    if users.find_one({'email': email}):
        flash('Email already exists', 'error')
    else:
        try:
            users.insert_one({'email': email, 'password': password})
            flash('Account created successfully!', 'success')
        except PyMongoError as e:
            print("Error inserting into MongoDB:", e)
            flash('An error occurred. Please try again.', 'error')
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('logged_in', None)  # Remove 'logged_in' from session
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)





