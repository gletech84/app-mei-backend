# app.py

import os
import psycopg2
from flask import Flask, request, jsonify
from flask_cors import CORS

# ==============================
# CONFIG
# ==============================

app = Flask(__name__)
CORS(app)

DATABASE_URL = os.getenv("DATABASE_URL")

# ==============================
# CONEXÃO
# ==============================

def get_connection():
    return psycopg2.connect(DATABASE_URL)

# ==============================
# HEALTH CHECK
# ==============================

@app.route("/")
def home():
    return jsonify({"status": "backend online"})

# ==============================
# CADASTRO DE USUÁRIO
# ==============================

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    email = data.get("email")

    if not email:
        return jsonify({"erro": "Email obrigatório"}), 400

    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            "INSERT INTO users (email) VALUES (%s) RETURNING id;",
            (email,)
        )

        user_id = cur.fetchone()[0]

        conn.commit()
        cur.close()
        conn.close()

        return jsonify({
            "status": "usuário criado",
            "user_id": user_id,
            "email": email
        })

    except psycopg2.errors.UniqueViolation:
        return jsonify({"erro": "Email já cadastrado"}), 400

    except Exception as e:
        return jsonify({"erro": str(e)}), 500

# ==============================
# LISTAR USUÁRIOS (TESTE)
# ==============================

@app.route("/users", methods=["GET"])
def listar_users():
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("SELECT id, email, plano, assinatura_ativa FROM users;")
        rows = cur.fetchall()

        users = []
        for r in rows:
            users.append({
                "id": r[0],
                "email": r[1],
                "plano": r[2],
                "assinatura_ativa": r[3]
            })

        cur.close()
        conn.close()

        return jsonify(users)

    except Exception as e:
        return jsonify({"erro": str(e)}), 500


# ==============================
# START (Render usa gunicorn)
# ==============================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
