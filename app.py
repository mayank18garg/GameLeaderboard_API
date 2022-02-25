#!/usr/bin/python
import sqlite3
from flask import Flask, request, jsonify
from flask_cors import CORS
# from flask_restful import APIException
from flask import abort

def connect_to_db():
    conn = sqlite3.connect('my_database.db')
    print("open database successfully")
    return conn


def create_db_table():
    try:
        conn = connect_to_db()
        c = conn.cursor()
        tables = c.execute("""SELECT name FROM sqlite_master WHERE type='table' AND name='users'""").fetchall()
        if tables != []:
            conn.execute('''DROP TABLE users''')
        conn.execute('''
            CREATE TABLE users (
                player_id INTEGER PRIMARY KEY NOT NULL,
                username TEXT NOT NULL,
                xp INTEGER DEFAULT 0 ,
                gold INTEGER DEFAULT 0
            )
        ''')

        conn.commit()
        print("User table created successfully")
    except:
        print("User table creation failed - Maybe table")
    finally:
        conn.close()


def insert_user(user):
    inserted_user = {}
    try:
        conn = connect_to_db()
        cur = conn.cursor()
        cur.execute("INSERT INTO users (username, xp, gold) VALUES (?, ?, ?)", (user['username'], 0,0) )
        conn.commit()
        # inserted_user = get_user_by_id(cur.lastrowid)
        player_id = cur.lastrowid
        cur.execute("SELECT username, player_id FROM users WHERE player_id = ?", (player_id,))
        row = cur.fetchone()
        inserted_user["username"] = row[0]
        inserted_user["player_id"] = row[1]
    except:
        conn().rollback()

    finally:
        conn.close()

    return inserted_user


def get_users():
    users = []
    try:
        conn = connect_to_db()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM users")
        rows = cur.fetchall()

        # convert row objects to dictionary
        for i in rows:
            user = {}
            user["player_id"] = i["player_id"]
            user["username"] = i["username"]
            user["xp"] = i["xp"]
            user["gold"] = i["gold"]
            users.append(user)

    except:
        users = []

    return users


def get_user_by_id(player_id):
    user = {}
    try:
        conn = connect_to_db()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE player_id = ?", (player_id,))
        row = cur.fetchone()

        # convert row object to dictionary
        user["player_id"] = row["player_id"]
        user["username"] = row["username"]
        user["xp"] = row["xp"]
        user["gold"] = row["gold"]
    except:
        user = {}

    return user


def update_user(user, player_id):
    updated_user = {}
    try:
        conn = connect_to_db()
        cur = conn.cursor()
        cur.execute("UPDATE users SET username = ?, xp = ?, gold = ? WHERE player_id =?", (user["username"], user["xp"], user["gold"], player_id,))
        conn.commit()
        #return the user
        updated_user = get_user_by_id(player_id)

    except:
        conn.rollback()
        # updated_user = {}
    finally:
        conn.close()

    return updated_user

def leaderboard(sortby,size):
    users = []
    try:
        conn = connect_to_db()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * from users ORDER BY {} DESC LIMIT {}".format(sortby,size))
        rows = cur.fetchall()
        for i in rows:
            user = {}
            user['username'] = i['username']
            user['player_id'] = i['player_id']
            user['gold'] = i['gold']
            user['xp'] = i['xp']
            users.append(user)
    except:
        users = []
    return users

users = []
user0 = {
    "username": "Mayank"
}

user1 = {
    "username": "Garg"
}

user2 = {
    "username": "Hogwarts"
}

user3 = {
    "username": "Gryffindor"
}

users.append(user0)
users.append(user1)
users.append(user2)
users.append(user3)

create_db_table()
# delete_db_table()
for i in users:
    print(insert_user(i))

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/api/player', methods=['GET'])
def api_get_users():
    return jsonify(get_users())

@app.route('/api/player/<player_id>', methods=['GET'])
def api_get_user(player_id):
    out_json = jsonify(get_user_by_id(player_id))
    if not out_json.json:
        return "Error 405: Player_id not found!"
    return out_json

@app.route('/api/v1/player',  methods = ['POST'])
def api_add_user():
    user = request.get_json()
    out_json = jsonify(insert_user(user))
    if not out_json.json:
        return "Error 405: Provide Username to create a new player in JSON!"
    return out_json

@app.route('/api/player/<player_id>',  methods = ['PUT'])
def api_update_user(player_id):
    user = request.get_json()
    out_json = jsonify(update_user(user,player_id))
    if not out_json.json:
        return "Error 405: Provide Username, player_id, xp and Gold in JSON to update the player's information!"
    return out_json

@app.route('/api/leaderboards', methods = ['GET'])
def api_leaderboard():
    args = request.args
    sortby = args.get('sortby')
    size = args.get('size')
    out_json = jsonify(leaderboard(sortby,size))
    if not out_json.json:
        return "Error 405: Provide valid Sortby:gold/xp and size as parameter!"
    return out_json

@app.route('/')
def index():
    return "Hello Players!"

@app.errorhandler(Exception)
def basic_error(e):
    return "an error occured: " + str(e)

if __name__ == "__main__":
    #app.debug = True
    # app.run(host="127.0.0.1")
    app.run(host="0.0.0.0", port=80)