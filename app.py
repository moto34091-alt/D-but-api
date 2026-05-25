from flask import Flask, request, render_template, redirect, session, jsonify
import sqlite3

app = Flask(__name__)
app.secret_key = "tiktok_creator_secret_key"

DB = "users.db"

# -------------------------
# INIT DB
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

# -------------------------
# DB HELPERS
# -------------------------
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


def get_user_by_name(username):
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
# IA SIMPLE (FREE)
# -------------------------
def generate(type):

    ideas = [
        "🎬 Transformation incroyable",
        "😂 Situation drôle du quotidien",
        "🔥 Astuce secrète inconnue",
        "📱 Application utile",
        "💡 Erreur que tout le monde fait",
        "🚀 Challenge viral TikTok",
        "😱 Histoire choquante",
        "💰 Astuce pour gagner de l'argent"
    ]

    scripts = [
        "HOOK: Attends stop !\nCONTENU: Voici un secret...\nFIN: Abonne-toi 🔥",
        "HOOK: Personne ne te dit ça...\nCONTENU: Voilà la vérité...\nFIN: Partage ça",
        "HOOK: Tu veux devenir viral ?\nCONTENU: Fais ça...\nFIN: Essaie maintenant"
    ]

    titles = [
        "🔥 Tu dois voir ça",
        "😱 Personne ne t’a dit ça",
        "🚀 Le secret viral",
        "💡 Astuce incroyable",
        "😂 Tu vas rire après ça"
    ]

    if type == "script":
        return scripts[0]

    if type == "title":
        return "\n".join(titles[:3])

    return ideas[0]


# -------------------------
# LOGIN
# -------------------------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = get_user(username, password)

        if user:
            session["user"] = username
            return redirect("/dashboard")

        return "❌ Login incorrect"

    return render_template("login.html")


# -------------------------
# REGISTER
# -------------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        create_user(username, password)
        return redirect("/")

    return render_template("register.html")


# -------------------------
# DASHBOARD
# -------------------------
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")

    user = get_user_by_name(session["user"])

    return render_template(
        "dashboard.html",
        user=user[1],
        referrals=user[3]
    )


# -------------------------
# SETTINGS
# -------------------------
@app.route("/settings")
def settings():
    if "user" not in session:
        return redirect("/")
    return render_template("settings.html", user=session["user"])


# -------------------------
# INVITE SYSTEM
# -------------------------
@app.route("/invite")
def invite():
    if "user" not in session:
        return redirect("/")

    username = session["user"]
    add_referral(username)

    return f"""
🎉 Lien de parrainage :

👉 https://tiktokcreator.up.railway.app/register?ref={username}

🔥 Partage pour gagner des utilisateurs !
"""


# -------------------------
# IA ROUTES
# -------------------------
@app.route("/idea", methods=["POST"])
def idea():
    return jsonify({"result": generate("idea")})


@app.route("/script", methods=["POST"])
def script():
    return jsonify({"result": generate("script")})


@app.route("/title", methods=["POST"])
def title():
    return jsonify({"result": generate("title")})


# -------------------------
# 10 POSTS VIRALS
# -------------------------
@app.route("/viral_10", methods=["POST"])
def viral_10():

    posts = []

    for i in range(10):
        post = f"""
🎬 POST {i+1}

💡 IDÉE: {generate("idea")}

🎥 SCRIPT: {generate("script")}

🔥 TITRE: {generate("title")}

#fyp #viral #tiktok
"""
        posts.append(post)

    return jsonify({"result": "\n\n-----------------\n\n".join(posts)})


# -------------------------
# LOGOUT
# -------------------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# -------------------------
# RUN
# -------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
