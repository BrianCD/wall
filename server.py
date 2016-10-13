color = True
from flask import Flask, render_template, redirect, request, session, flash
from flask_bcrypt import Bcrypt
import randomcolor
import os
import re
# import the Connector function
from sqlhelper import MySQLConnection
app = Flask(__name__)
app.secret_key = os.urandom(24)

bcrypt = Bcrypt(app)
# connect and store the connection in "mysql" note that you pass the database name to the function
mysql = MySQLConnection(app, 'wall')
colorer = randomcolor.RandomColor()

@app.route("/")
def index():
    if "id" in session:
        return redirect("/wall")
    return render_template("index.html")

@app.route("/login", methods = ["POST"])
def login():
    form = request.form
    user = mysql.query_db("select id, password, first_name, last_name from users where email = :email", {"email":form["email"]})
    if not user:
        flash("User not found")
        return redirect("/")
    if not bcrypt.check_password_hash(user[0]["password"], form["password"]):
        flash("Invalid password")
        return redirect("/")
    session["id"] = user[0]["id"]
    session["name"] = user[0]["first_name"]+" "+user[0]["last_name"]
    print session["id"]
    return redirect("/wall")

@app.route("/register", methods = ["POST"])
def register():
    form = request.form
    valid = True
    if not all (form[k] for k in ("first", "last", "email", "password", "passconf")):
        flash("All fields are mandatory")
        redirect("/")
    if not form["first"].isalpha():
        flash("First name must contain only alphabetical characters.")
        valid = False;
    if not form["last"].isalpha():
        flash("Last name must contain only alphabetical characters.")
        valid = False;
    if not re.match(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$',form["email"]):
        flash("Email must be valid.")
        valid = False;
    if form["password"] != form["passconf"]:
        flash("Password must match confirmation.")
        valid = False;
    if valid:
        mysql.query_db("insert into users(first_name, last_name, email, password, color) values (:first, :last, :email, :pass, :color)",{"first":form["first"], "last":form["last"], "email":form["email"], "pass":bcrypt.generate_password_hash(form["password"]), "color":colorer.generate(luminosity = "bright")})
        flash("Success. You may now log in.")
    return redirect("/")



@app.route("/wall")
def wall():
    if not "id" in session:
        flash("You are not logged in.")
        return redirect("/")
    messages = mysql.query_db("select message, messages.created_at as created_at, first_name, last_name, messages.id, messages.color as mcolor, users.color as bcolor from messages join users on users.id = user_id order by messages.created_at desc")
    for message in messages:
        message["comments"] = mysql.query_db("select comment, comments.created_at, first_name, last_name, comments.color as ccolor, users.color as bcolor from comments join users on users.id = user_id where message_id = :id order by comments.created_at desc", {"id":message["id"]})
    return render_template("wall.html", messages = messages, col = color, name = session["name"])

@app.route("/post", methods = ["POST"])
def post():
    mysql.query_db("insert into messages(message, user_id, color) values (:message, :id, :color)",{"message":request.form["post"], "color":colorer.generate(luminosity = "bright"), "id":session["id"]})
    return redirect("/")

@app.route("/post/<message>", methods = ["POST"])
def post_comment(message):
    mysql.query_db("insert into comments(comment, user_id, message_id, color) values (:comment, :id, :message, :color)",{"comment":request.form["post"], "message":message, "color":colorer.generate(luminosity = "bright"), "id":session["id"]})
    return redirect("/")

@app.route("/logout")
def logout():
    del session["id"], session["name"]
    return redirect("/")

app.run(debug=True)
