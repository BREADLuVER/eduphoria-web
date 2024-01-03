from flask import Flask, render_template, request, redirect, url_for, flash
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from pymongo.errors import PyMongoError
from flask_mail import Message, Mail
import os
from flask import session

app = Flask(__name__)
app.secret_key = '246810' 
app.config['SECURITY_PASSWORD_SALT'] = os.getenv('SECURITY_PASSWORD_SALT')

app.config['MAIL_SERVER'] = 'live.smtp.mailtrap.io'
app.config['MAIL_PORT'] = 587

MAIL_UN = os.getenv('MAIL_USERNAME')
MAIL_P = os.getenv('MAIL_PASSWORD')
app.config['MAIL_USERNAME'] = MAIL_UN
app.config['MAIL_PASSWORD'] = MAIL_P
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

mail = Mail(app)

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

def send_password_reset_email(email_to, reset_token):
    msg = Message("Password Reset Request",
                  sender="noreply@example.com",  # Sender email
                  recipients=[email_to])
    msg.body = f"""To reset your password, visit the following link:
    {url_for('reset_token', token=reset_token, _external=True)}

    If you did not make this request, simply ignore this email and no changes will be made.
    """
    mail.send(msg)

def generate_reset_token(email):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    return serializer.dumps(email, salt=app.config['SECURITY_PASSWORD_SALT'])

@app.route('/forgot', methods=['POST'])
def forgot_password():
    email = request.form.get('email')
    user = users.find_one({'email': email})  # Assuming 'users' is your MongoDB collection
    if user:
        reset_token = generate_reset_token(email)
        send_password_reset_email(email, reset_token)
        flash('An email has been sent with instructions to reset your password.', 'info')
    else:
        flash('No account found with that email address.', 'error')
    # Redirect back to the same page so the user can see the flash message
    return redirect(url_for('index'))

@app.route('/reset/<token>', methods=['GET', 'POST'])
def reset_token(token):
    try:
        serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
        email = serializer.loads(token, salt=app.config['SECURITY_PASSWORD_SALT'], max_age=3600)
    except SignatureExpired:
        # The token is expired
        flash('The password reset link is expired.', 'danger')
        return redirect(url_for('forgot_password'))

    if request.method == 'POST':
        password = request.form['password']
        hashed_password = generate_password_hash(password)
        # Assuming users is your MongoDB collection for user accounts
        users.update_one({'email': email}, {'$set': {'password': hashed_password}})
        flash('Your password has been updated!', 'success')
        return redirect(url_for('login'))
    
    return render_template('reset_password.html', token=token)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)





