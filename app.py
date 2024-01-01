import os
import mongomock
from flask import Flask, render_template, request, redirect, url_for
from pymongo.mongo_client import MongoClient
from pymongo import DESCENDING
from hashlib import sha256
from github_api import *
from datetime import datetime
from bson import ObjectId
GITHUB_TOKEN = os.getenv("TOKEN")

app = Flask(__name__)

if os.getenv("TESTING"):
    app.config["MONGO_CONN"] = mongomock.MongoClient()
else:
    URI = "mongodb://mongodb:27017/"
    app.config["MONGO_CONN"] = MongoClient(URI)

connection = app.config["MONGO_CONN"]
db = connection["blog"]
blogs = db.blogs
users = db.users

@app.route("/")
def show_login():
    return render_template("login.html")

@app.route("/", methods=["POST"])
def login():
    username = request.form["username"]
    password = sha256(request.form["password"].encode()).hexdigest()
    data = users.find_one({"username": username})
    if data is None:
        return render_template("login.html", error = True)
    if data["password"] == password:
        return redirect(url_for("show_home", username = username))
    return render_template("login.html", error = True)

@app.route("/register")
def show_register():
    return render_template("register.html")

@app.route("/register", methods=["POST"])
def register():
    username = request.form["username"]
    password = sha256(request.form["password"].encode()).hexdigest()
    user_details = get_github_user_details(username, GITHUB_TOKEN)
    rating = calculate_rating(user_details)
    joke = get_feedback(username, rating) 
    if user_details is None:
        return render_template("register.html", error = True)   
    doc = {
        "username": username,
        "password": password,
        "friends": []
    }

    blog = {
        "owner": username,
        "title": username + " has joined the community!!!! 👏",
        "main_body": joke,
        "time": datetime.now()
    }
    users.insert_one(doc)   
    blogs.insert_one(blog)
    return render_template("register.html", success = True)  

@app.route("/home/<username>")
def show_home(username):
    user_details = get_github_user_details(username, GITHUB_TOKEN)
    rating = calculate_rating(user_details)
    joke = get_feedback(username, rating) 
    return render_template("home.html", username = username, rating = rating, joke = joke)

@app.route("/myblogs/<username>")
def show_myblogs(username):
    myblogs = blogs.find({"owner": username})
    myblogs = sorted(myblogs, key=lambda item: item['time'], reverse=True)
    return render_template("myblogs.html", username = username, myblogs = myblogs)

@app.route("/myblogs/<username>", methods=["POST"])
def post_blog(username):
    owner = username
    title = request.form["title"]
    main_body = request.form["main_body"]

    doc = {
        "owner": owner,
        "title": title,
        "main_body": main_body,
        "time": datetime.now()
    }
    blogs.insert_one(doc)
    return redirect(url_for("show_myblogs", username = username))

@app.route("/friendblogs/<username>")
def show_friendblogs(username):
 
    user = users.find_one({"username": username})

    friends = user["friends"]
    all_friend_blogs = []
    for friend in friends:
        friend_blogs = blogs.find({"owner": friend})
        all_friend_blogs.extend(friend_blogs)
    all_friend_blogs = sorted(all_friend_blogs, key=lambda item: item['time'], reverse=True)
    if all_friend_blogs == []:
          return render_template('friendblogs.html', username = username, quiet = True)
    return render_template('friendblogs.html', friend_blogs = all_friend_blogs, username = username)

@app.route("/allblogs/<username>")
def show_allblogs(username):
    all_blogs = blogs.find({}).sort('time', DESCENDING)
    return render_template('allblogs.html', all_blogs = all_blogs, username = username)

@app.route("/addfriend/<username>")
def show_addfriend(username):
    return render_template("addfriend.html", username = username)

@app.route("/addfriend/<username>", methods= ["POST"])
def addfriend(username):
    friend = request.form["friend"]
    if users.find_one({"username": friend}) is None:
        return render_template("addfriend.html", username = username, error = True)
    query = {"username": username, "friends": {"$in": [friend]}}
    if users.find_one(query) is not None:
        return render_template("addfriend.html", username = username, exist = True)
    users.update_one({"username": username}, {"$push": {"friends": friend}})
    return render_template("addfriend.html", username = username, success = True)

@app.route("/checkout/<username>")
def show_checkout(username):
    return render_template("checkout.html", username  = username)

@app.route("/checkout/<username>", methods=["POST"])
def checkout(username):
    account = request.form["username"]
    user_details = get_github_user_details(account, GITHUB_TOKEN)
    if user_details is None:
         return render_template("checkout.html", username  = username, error = True)
    rating = calculate_rating(user_details)
    joke = get_feedback(account, rating) 
    return render_template("checkout.html", username  = username, rating = rating, joke = joke, account = account, result = True)

@app.route("/delete_blogpost", methods=["POST"])
def delete_blogpost():
    id = ObjectId(request.form["id"])
    username = request.form["owner"]
    print(id)
    blogs.delete_one({"_id": id})
    return redirect(url_for("show_myblogs", username = username))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
