from flask import Flask, render_template, request, redirect, session, flash
from flask_bcrypt import Bcrypt

import datetime

from mysqlconnection import MySQLConnector

app = Flask(__name__)
app.secret_key = "another_wall"

mysql = MySQLConnector("another_wall")
bcrypt = Bcrypt(app)

@app.route("/")
def login_page():
	return render_template("login.html")

@app.route("/register", methods=["POST"])
def register():
	if request.form["password"] != request.form["confirm"]:
		flash("Passwords don't match")
	else:
		query = "INSERT INTO users (first_name, last_name, username, password, created_at, updated_at) VALUES ('{}', '{}', '{}', '{}', NOW(), NOW())".format(request.form["first_name"], request.form["last_name"], request.form["username"], str(bcrypt.generate_password_hash(request.form["password"]))[2:-1])
		# data = {
		# 	"first_name": request.form["first_name"],
		# 	"last_name": request.form["last_name"],
		# 	"email": request.form["email"],
		# 	"password": str(bcrypt.generate_password_hash(request.form["password"]))[2:-1],
		# }
		print(query)
		mysql.run_mysql_query(query)

		query = "SELECT id FROM users WHERE username='{}'".format(request.form["username"])
		new_user = mysql.fetch(query)[0]
		session["user_id"] = new_user["id"]
		print(session["user_id"])
		
	return redirect("/")

@app.route("/login", methods=["POST"])
def login():
	user = mysql.fetch("SELECT * FROM users WHERE username='{}'".format(request.form["username"]))
	if not user:
		flash("Username doesn't exist")
		return redirect("/")
	else:
		user = user[0]

	if bcrypt.check_password_hash(user["password"], request.form["password"]):
		session["user_id"] = user["id"]
	else:
		flash("Password incorrect")

	return redirect("/")

@app.route("/wall")
def wall():
	user = mysql.fetch("SELECT * FROM users WHERE id={}".format(session["user_id"]))[0]

	query = "SELECT messages.message, messages.created_at, messages.id, messages.user_id, users.first_name FROM messages LEFT JOIN users ON users.id=messages.user_id ORDER BY messages.updated_at DESC"

	messages = mysql.fetch(query)

	query = "SELECT comments.comment, comments.created_at, comments.message_id, users.first_name, comments.user_id, comments.id FROM comments LEFT JOIN users ON users.id=comments.user_id"

	comments = mysql.fetch(query)

	comment_dict = {}

	for comment in comments:
		if int(comment.user_id) == int(session["user_id"]) and datetime.datetime.now() - comment.created_at <= datetime.timedelta(minutes=30):
			comment["can_delete"] = True
		else:
			comment["can_delete"] = False
			
		if comment["message_id"] in comment_dict:
			comment_dict[comment["message_id"]].append(comment)
		else:
			comment_dict[comment["message_id"]] = [comment]
	
	for message in messages:
		if message["id"] in comment_dict:
			message["comments"] = comment_dict[message["id"]]
		else:
			message["comments"] = []

	# for message in messages:
	# 	query = "SELECT comments.comment, comments.created_at, comments.message_id, users.first_name FROM comments LEFT JOIN users ON users.id=comments.user_id WHERE comments.message_id={}".format(message["id"])
	# 	message["comments"] = mysql.fetch(query)

	return render_template("wall.html", user=user, messages=messages)

@app.route("/message", methods=["POST"])
def message():
	message = request.form["message"].replace("'", "''")

	query = "INSERT INTO messages (message, user_id, created_at, updated_at) VALUES ('{}', '{}', NOW(), NOW())".format(message, session["user_id"])

	mysql.run_mysql_query(query)

	return redirect("/wall")

@app.route("/comment", methods=["POST"])
def comment():
	query = "INSERT INTO comments (comment, user_id, message_id, created_at, updated_at) VALUES ('{}', '{}', '{}', NOW(), NOW())".format(request.form["comment"].replace("'", "''"), session["user_id"], request.form["message_id"])

	mysql.run_mysql_query(query)

	return redirect("/wall")

@app.route("/delete_comment", methods=["POST"])
def delete_comment():
	comment = mysql.fetch("SELECT comments.user_id, comments.created_at FROM comments WHERE comments.id={}".format(request.form["comment_id"]))[0]

	if comment["user_id"] == session["user_id"] and datetime.datetime.now() - comment["created_at"] <= datetime.timedelta(minutes=30):
		query = "DELETE FROM comments WHERE comments.id={}".format(request.form["comment_id"])
		mysql.run_mysql_query(query)
	else:
		flash("Nice try, guy")

	return redirect("/wall")

@app.route("/delete_message", methods=["POST"])
def delete_message():
	query = "DELETE FROM comments WHERE comments.message_id={}".format(request.form["message_id"])

	mysql.run_mysql_query(query)

	query = "DELETE FROM messages WHERE messages.id={}".format(request.form["message_id"])
	mysql.run_mysql_query(query)
	return redirect("/wall")

app.run(debug=True)