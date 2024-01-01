from flask import Flask, render_template, request, redirect, url_for
from flask_pymongo import PyMongo
from flask import flash

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)

app.config["MONGO_URI"] = "your_mongodb_uri"
mongo = PyMongo(app)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Logic for registration
        # Insert user data into MongoDB
        pass
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Logic for login
        # Check user data in MongoDB
        pass
    return render_template('login.html')
