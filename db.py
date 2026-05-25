import sqlite3

def init_db():
    conn = sqlite3.connect("users.db")
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

def create_user(username, password):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()

    try:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
    except:
        pass

    conn.close()

def get_user(username, password):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()

    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = c.fetchone()

    conn.close()
    return user

def is_premium(username):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()

    c.execute("SELECT premium FROM users WHERE username=?", (username,))
    user = c.fetchone()

    conn.close()

    return user and user[0] == 1
