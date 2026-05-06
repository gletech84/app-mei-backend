from database.db import get_conn

def criar_usuario(email):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO users (email)
        VALUES (%s)
        ON CONFLICT (email) DO NOTHING
    """, (email,))

    conn.commit()
    cur.close()
    conn.close()


def buscar_usuario(email):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT id, email, plano, assinatura_ativa FROM users WHERE email=%s", (email,))
    user = cur.fetchone()

    cur.close()
    conn.close()

    return user


def ativar_assinatura(email):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        UPDATE users
        SET assinatura_ativa = TRUE,
            plano = 'pro'
        WHERE email=%s
    """, (email,))

    conn.commit()
    cur.close()
    conn.close()
