from flask import Flask, request, render_template, redirect, session, jsonify
import sqlite3

app = Flask(__name__)
app.secret_key = "secret123"

DB = "users.db"


# -------------------------
# DB INIT
# -------------------------
def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        referrals INTEGER DEFAULT 0
    )
    """)

    conn.commit()
    conn.close()

init_db()


def create_user(username, password):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
    except:
        pass
    conn.close()


def get_user(username, password):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = c.fetchone()
    conn.close()
    return user


def get_user_data(username):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=?", (username,))
    user = c.fetchone()
    conn.close()
    return user


def add_referral(username):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("UPDATE users SET referrals = referrals + 1 WHERE username=?", (username,))
    conn.commit()
    conn.close()


# -------------------------
# LOGIN
# -------------------------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]

        user = get_user(u, p)

        if user:
            session["user"] = u
            return redirect("/dashboard")

        return "❌ Login incorrect"

    return render_template("login.html")


# -------------------------
# REGISTER
# -------------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]

        create_user(u, p)
        return redirect("/")

    return render_template("register.html")


# -------------------------
# DASHBOARD DATA
# -------------------------
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")

    user = get_user_data(session["user"])

    return render_template("dashboard.html",
                           user=user[1],
                           referrals=user[3])


# -------------------------
# VIRAL SYSTEM (REF LINK)
# -------------------------
@app.route("/invite")
def invite():
    if "user" not in session:
        return redirect("/")

    username = session["user"]
    add_referral(username)

    return f"""
    🎉 Merci pour ton partage !

    Ton lien :
    👉 https://tonsite.com/register?ref={username}
    """


# -------------------------
# LOGOUT
# -------------------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
