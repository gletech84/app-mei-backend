import sqlite3

def init_db():
    conn = sqlite3.connect("saas.db")
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT,
        senha TEXT,
        plano TEXT,
        ativo INTEGER DEFAULT 0
    )
    """)

    conn.commit()
    conn.close()


def get_user(email, senha):
    conn = sqlite3.connect("saas.db")
    c = conn.cursor()

    c.execute("SELECT * FROM users WHERE email=? AND senha=?", (email, senha))
    user = c.fetchone()

    conn.close()
    return user
