from flask import Flask, render_template, request
import sqlite3

DATABASE = 'db.sqlite'

app = Flask(__name__)

def connect_db():
         return sqlite3.connect(DATABASE)

def init_db():
    with connect_db() as con:
        con.execute("""CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    name TEXT
                    )""")
        con.commit()

def create_user(name):
    with connect_db() as con:
        con.execute("INSERT INTO users (name) VALUES (?)", (name,))

def get_users():
    with connect_db() as con:
        cursor = con.execute("SELECT * FROM users")
        return cursor.fetchall()

def get_user(id):
    with connect_db() as con:
        cursor = con.execute("SELECT * FROM users WHERE id = ?", (id,))
        return cursor.fetchone()

def update_user(id, name):
    with connect_db() as con:
        con.execute("UPDATE users SET name = ? WHERE id = ?", (name, id))


def delete_user(id):
    with connect_db() as con:
        con.execute("DELETE FROM users WHERE id = ?", (id,))

# @app.route("/")
# def hello():
#     return "Hello World!"

@app.route("/")
def index():
    users = get_users()
    return render_template("index.html", users=users)

@app.route("/add_user", methods=["POST"])
def add_user():
    name = request.form.get("name")
    create_user(name)
    return "Data added successfully!"


if __name__ == "__main__":
    init_db()
    app.run()