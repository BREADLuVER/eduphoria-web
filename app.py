from flask import Flask, render_template, request, redirect, url_for, flash
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Set a secret key for message flashing

# MongoDB configuration
app.config["MONGO_URI"] = "your_mongodb_uri"
mongo = PyMongo(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        users = mongo.db.users
        existing_user = users.find_one({'email': request.form['email']})

        if existing_user is None:
            hashpass = generate_password_hash(request.form['password'])
            users.insert_one({'email': request.form['email'], 'password': hashpass})
            flash('Account created successfully!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Email already registered.', 'error')

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        users = mongo.db.users
        login_user = users.find_one({'email': request.form['email']})

        if login_user:
            if check_password_hash(login_user['password'], request.form['password']):
                flash('Logged in successfully!', 'success')
                return redirect(url_for('index'))
            else:
                flash('Invalid password.', 'error')
        else:
            flash('Email not registered.', 'error')

    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)

