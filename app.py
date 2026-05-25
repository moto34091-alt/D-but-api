from flask import Flask, request, render_template, redirect, session, jsonify
import os
import sqlite3
from openai import OpenAI

app = Flask(__name__)
app.secret_key = "secret123"

# 🔑 OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# -------------------------
# 🧠 DATABASE FUNCTIONS
# -------------------------
DB_NAME = "users.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        premium INTEGER DEFAULT 0
    )
    """)

    conn.commit()
    conn.close()

init_db()


def create_user(username, password):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    try:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
    except:
        pass

    conn.close()


def get_user(username, password):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = c.fetchone()

    conn.close()
    return user


def is_premium(username):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("SELECT premium FROM users WHERE username=?", (username,))
    user = c.fetchone()

    conn.close()

    return user and user[0] == 1


# -------------------------
# 🤖 IA FUNCTION
# -------------------------
def generate(prompt):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Tu es expert en contenu viral TikTok."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content


# -------------------------
# 🔐 LOGIN
# -------------------------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = get_user(username, password)

        if user:
            session["user"] = username
            return redirect("/dashboard")
        else:
            return "❌ Login incorrect"

    return render_template("login.html")


# -------------------------
# 📝 REGISTER
# -------------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        create_user(username, password)
        return redirect("/")

    return render_template("register.html")


# -------------------------
# 🌐 DASHBOARD
# -------------------------
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")

    return render_template("dashboard.html", user=session["user"])


# -------------------------
# 🤖 IA ROUTES (FIXED)
# -------------------------
@app.route("/idea", methods=["POST"])
def idea():
    try:
        return jsonify({"result": generate("Donne une idée TikTok virale.")})
    except:
        return jsonify({"result": "❌ Erreur IA"})


@app.route("/script", methods=["POST"])
def script():
    try:
        return jsonify({"result": generate("Écris un script TikTok viral.")})
    except:
        return jsonify({"result": "❌ Erreur IA"})


@app.route("/title", methods=["POST"])
def title():
    try:
        return jsonify({"result": generate("Donne 5 titres TikTok viraux.")})
    except:
        return jsonify({"result": "❌ Erreur IA"})


# -------------------------
# 🚪 LOGOUT
# -------------------------
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")


# -------------------------
# 🚀 RUN APP
# -------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
