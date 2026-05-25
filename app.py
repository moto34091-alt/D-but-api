from flask import Flask, request, render_template, redirect, session, jsonify
import os
from openai import OpenAI
import db

app = Flask(__name__)
app.secret_key = "supersecretkey"

db.init_db()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# 🤖 IA FUNCTION
def generate(prompt):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Tu es expert en contenu viral TikTok."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content


# 🔐 LOGIN
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = db.get_user(username, password)

        if user:
            session["user"] = username
            return redirect("/dashboard")
        else:
            return "❌ Login incorrect"

    return render_template("login.html")


# 📝 REGISTER
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        db.create_user(username, password)
        return redirect("/")

    return render_template("register.html")


# 🌐 DASHBOARD
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")

    return render_template("dashboard.html", user=session["user"])


# 🤖 IA ROUTES
@app.route("/idea", methods=["POST"])
def idea():
    return jsonify({"result": generate("Donne une idée TikTok virale.")})


@app.route("/script", methods=["POST"])
def script():
    return jsonify({"result": generate("Écris un script TikTok viral.")})


@app.route("/title", methods=["POST"])
def title():
    return jsonify({"result": generate("Donne 5 titres TikTok viraux.")})


# 🚪 LOGOUT
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
