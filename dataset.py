import randomcolor
from sqlhelper import MySQLConnection
from flask import Flask
from flask_bcrypt import Bcrypt
app = Flask(__name__)
mysql = MySQLConnection(app, 'wall')
bcrypt = Bcrypt(app)
colorer = randomcolor.RandomColor()
from random import randrange

mysql.query_db("delete from comments")
mysql.query_db("delete from messages")
mysql.query_db("delete from users")

for x in range(10):
    mysql.query_db("insert into users(first_name, last_name, email, password, color) values (:first, :last, :email, :pass, :color)",{"first":"User", "last":x, "email":str(x)+"@dummy.com", "pass":bcrypt.generate_password_hash(str(x)), "color":colorer.generate(luminosity = "bright")[0]})
    ids = mysql.query_db("select id from users")
for x in range(30):
    mysql.query_db("insert into messages(message, user_id, color) values (:message, :id, :color)",{"message":"Message "+str(x), "color":colorer.generate(luminosity = "bright")[0], "id":ids[randrange(10)]["id"]})
    mids = mysql.query_db("select id from messages")
for x in range(100):
    mysql.query_db("insert into comments(comment, user_id, message_id, color) values (:message, :id, :mid, :color)",{"message":"Comment "+str(x), "color":colorer.generate(luminosity = "bright")[0], "id":ids[randrange(10)]["id"], "mid":mids[randrange(30)]["id"]})
