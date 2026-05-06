from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
import os
import jwt
from datetime import datetime, timedelta
from functools import wraps

app = Flask(__name__)
CORS(app)

SECRET_KEY = os.getenv("SECRET_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")


# =========================
# CONEXÃO BANCO
# =========================
def get_connection():
    return psycopg2.connect(DATABASE_URL)


# =========================
# CRIAR TOKEN JWT
# =========================
def gerar_token(email):
    payload = {
        "email": email,
        "exp": datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


# =========================
# DECORATOR AUTH
# =========================
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization")

        if not token:
            return jsonify({"erro": "Token ausente"}), 401

        try:
            token = token.split(" ")[1]
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            request.email = data["email"]
        except:
            return jsonify({"erro": "Token inválido"}), 401

        return f(*args, **kwargs)

    return decorated


# =========================
# DECORATOR PREMIUM
# =========================
def premium_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization")

        if not token:
            return jsonify({"erro": "Token ausente"}), 401

        try:
            token = token.split(" ")[1]
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            email = data["email"]

            conn = get_connection()
            cur = conn.cursor()

            cur.execute("SELECT plano FROM users WHERE email = %s", (email,))
            user = cur.fetchone()

            cur.close()
            conn.close()

            if not user:
                return jsonify({"erro": "Usuário não encontrado"}), 404

            plano = user[0]

            if plano != "premium":
                return jsonify({"erro": "Acesso apenas para premium"}), 403

        except:
            return jsonify({"erro": "Token inválido"}), 401

        return f(*args, **kwargs)

    return decorated


# =========================
# SETUP BANCO (FASE 13)
# =========================
@app.route("/setup-db")
def setup_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    ALTER TABLE users ADD COLUMN IF NOT EXISTS plano TEXT DEFAULT 'free';
    """)

    conn.commit()
    cur.close()
    conn.close()

    return {"status": "coluna plano criada"}


# =========================
# REGISTER
# =========================
@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    email = data.get("email")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO users (email)
    VALUES (%s)
    ON CONFLICT (email) DO NOTHING
    RETURNING id;
    """, (email,))

    user = cur.fetchone()

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({
        "status": "usuário criado",
        "email": email,
        "user_id": user[0] if user else None
    })


# =========================
# LOGIN
# =========================
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cur.fetchone()

    cur.close()
    conn.close()

    if not user:
        return jsonify({"erro": "Usuário não encontrado"}), 404

    token = gerar_token(email)

    return jsonify({"token": token})


# =========================
# ROTA PROTEGIDA
# =========================
@app.route("/perfil")
@token_required
def perfil():
    return jsonify({
        "status": "acesso autorizado",
        "usuario": request.email
    })


# =========================
# ROTA PREMIUM
# =========================
@app.route("/premium")
@premium_required
def premium():
    return jsonify({
        "msg": "Bem-vindo ao plano premium"
    })


# =========================
# HOME
# =========================
@app.route("/")
def home():
    return {"status": "SaaS rodando 🚀"}


# =========================
# RUN
# =========================
if __name__ == "__main__":
    app.run(debug=True)
