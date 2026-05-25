from flask import Flask, request, render_template, redirect, session, jsonify
import sqlite3
import random

app = Flask(__name__)
app.secret_key = "secret123"

DB_NAME = "users.db"

# -------------------------
# 🧠 DATABASE
# -------------------------
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
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


# -------------------------
# 🤖 IA GRATUITE (SIMULÉE)
# -------------------------
def generate(prompt):

    ideas = [
        "🎬 Fais une vidéo avant/après transformation",
        "😂 Situation drôle du quotidien",
        "🔥 Astuce inconnue que personne ne partage",
        "📱 Top 3 applications utiles",
        "🚀 Défi viral à lancer aujourd’hui",
        "💡 Erreur que tout le monde fait sur TikTok",
        "😱 Histoire choquante courte",
        "💰 Astuce pour gagner de l’argent en ligne"
    ]

    scripts = [
        "Hook: Attends, tu fais encore ça ?\nContenu: Voici pourquoi c’est une erreur...\nFin: Abonne-toi pour plus.",
        "Hook: Personne ne parle de ça...\nContenu: Voici la vérité...\nFin: Partage si tu ne savais pas.",
        "Hook: Tu veux devenir viral ?\nContenu: Fais ça en 3 étapes simples...\nFin: Essaie aujourd’hui."
    ]

    titles = [
        "🔥 Tu dois absolument voir ça",
        "😱 Personne ne t’a dit ça",
        "🚀 Le secret des vidéos virales",
        "💡 Astuce incroyable TikTok",
        "😂 Tu vas rire après ça"
    ]

    if "script" in prompt.lower():
        return random.choice(scripts)

    if "titre" in prompt.lower() or "title" in prompt.lower():
        return "\n".join(random.sample(titles, 3))

    return random.choice(ideas)


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
# 🤖 API
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
# 🚪 LOGOUT
# -------------------------
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")


# -------------------------
# 🚀 RUN
# -------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
