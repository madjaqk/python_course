from flask import Flask, render_template, request, redirect, session, flash
from mysqlconnection import MySQLConnector
from flask.ext.bcrypt import Bcrypt
import datetime
import re

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key = "wall-wall-wall"
mysql = MySQLConnector("wall_three")
EmailRegex = re.compile(r'^[a-zA-Z0-9\.\+_-]+@[a-zA-Z0-9\._-]+\.[a-zA-Z]*$')

@app.route("/")
def show_login_page():
    try:
        session["id"]
        return redirect("/wall")
    except:
        return render_template("login.html")

@app.route("/create", methods=["POST"])
def create_user():
    data = request.form
    errors = []

    if not data["first_name"]:
        errors.append("First name missing")

    if not data["last_name"]:
        errors.append("Last name missing")

    if not data["email"]:
        errors.append("E-mail missing")
    elif not EmailRegex.match(data["email"]):
        errors.append("Invalid E-mail address")
    elif len(mysql.fetch("SELECT * FROM users WHERE email='{}'".format(data["email"]))) > 0:
        errors.append("E-mail address already in use")

    if len(data["password"]) < 8:
        errors.append("Password too short")
    elif data["password"] != data["confirm"]:
        errors.append("Passwords do not match")

    if errors:
        for error in errors: flash(error)
        return redirect("/")
    else:
        password = bcrypt.generate_password_hash(data["password"])
        #password = str(password)[2:-1]
        query = 'INSERT INTO users (first_name, last_name, email, password, created_at, updated_at) VALUES ("{}", "{}", "{}", "{}", NOW(), NOW())'.format(data["first_name"], data["last_name"], data["email"], password)
        mysql.run_mysql_query(query)
        
        user = mysql.fetch("SELECT * FROM users WHERE email='{}'".format(data["email"]))[0]
        session["id"] = user["id"]
        return redirect("/wall")

@app.route("/login", methods=["POST"])
def login():
    query = "SELECT * FROM users WHERE email='{}'".format(request.form["email"])
    user = mysql.fetch(query)
    if not user:
        flash("User not found")
        return redirect("/")
    else:
        user = user[0]

    if bcrypt.check_password_hash(user["password"], request.form["password"]):
        session["id"] = user["id"]
        return redirect("/wall")
    else:
        flash("Incorrect password")
        return redirect("/")
        
@app.route("/wall")
def wall():
    try:
        session["id"]
    except:
        return redirect("/")
    
    logged_in_user = mysql.fetch("SELECT * FROM users WHERE id={}".format(session["id"]))[0]

    # Get all messages
    messages = mysql.fetch("SELECT message, first_name, messages.id, messages.created_at, messages.user_id FROM messages LEFT JOIN users ON messages.user_id=users.id ORDER BY messages.created_at DESC")

    # Get all comments
    
    return render_template("wall.html", name=logged_in_user["first_name"], messages=messages)

@app.route("/message", methods=["POST"])
def message():
    if request.form["message"]:
        message = request.form["message"].replace("'", "''")
        query = "INSERT INTO messages (message, user_id, created_at, updated_at) VALUES ('{}', '{}', NOW(), NOW())".format(message, session["id"])
        mysql.run_mysql_query(query)
    return redirect("/wall")

@app.route("/comment", methods=["POST"])
def comment():
    if request.form["comment"]:
        comment = request.form["comment"].replace("'", "''")
        query = "INSERT INTO comments (comment, user_id, message_id, created_at, updated_at) VALUES ('{}', '{}', '{}', NOW(), NOW())".format(comment, session["id"], request.form["message_id"])
        mysql.run_mysql_query(query)
    return redirect("/wall")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


app.run(debug=True)
