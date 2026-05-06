# app.py

import os
import psycopg2
import jwt
import datetime

from flask import Flask, request, jsonify
from flask_cors import CORS
from functools import wraps

# ==============================
# CONFIG
# ==============================

app = Flask(__name__)
CORS(app)

DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY")

# ==============================
# CONEXÃO
# ==============================

def get_connection():
    return psycopg2.connect(DATABASE_URL)

# ==============================
# JWT DECORATOR
# ==============================

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if "Authorization" in request.headers:
            token = request.headers["Authorization"].split(" ")[1]

        if not token:
            return jsonify({"erro": "Token ausente"}), 401

        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            current_user = data["email"]
        except Exception:
            return jsonify({"erro": "Token inválido"}), 401

        return f(current_user, *args, **kwargs)

    return decorated

# ==============================
# HEALTH CHECK
# ==============================

@app.route("/")
def home():
    return jsonify({"status": "backend online com JWT"})

# ==============================
# CADASTRO
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
# LOGIN (GERA TOKEN)
# ==============================

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")

    if not email:
        return jsonify({"erro": "Email obrigatório"}), 400

    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("SELECT id FROM users WHERE email=%s;", (email,))
        user = cur.fetchone()

        cur.close()
        conn.close()

        if not user:
            return jsonify({"erro": "Usuário não encontrado"}), 404

        token = jwt.encode({
            "email": email,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }, SECRET_KEY, algorithm="HS256")

        return jsonify({
            "token": token
        })

    except Exception as e:
        return jsonify({"erro": str(e)}), 500

# ==============================
# ROTA PROTEGIDA
# ==============================

@app.route("/perfil", methods=["GET"])
@token_required
def perfil(current_user):
    return jsonify({
        "status": "acesso autorizado",
        "usuario": current_user
    })

# ==============================
# LISTAR USERS (PROTEGIDO)
# ==============================

@app.route("/users", methods=["GET"])
@token_required
def listar_users(current_user):
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
# START
# ==============================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
