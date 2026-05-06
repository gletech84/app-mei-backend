from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import psycopg2
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
# JWT
# =========================
def gerar_token(email):
    payload = {
        "email": email,
        "exp": datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


# =========================
# MIDDLEWARE AUTH
# =========================
def token_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
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

    return wrapper


# =========================
# REGISTER
# =========================
@app.route("/register", methods=["POST"])
def register():
    email = request.json.get("email")

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
    email = request.json.get("email")

    token = gerar_token(email)

    return jsonify({"token": token})


# =========================
# PERFIL PROTEGIDO
# =========================
@app.route("/perfil")
@token_required
def perfil():
    return jsonify({
        "status": "acesso autorizado",
        "usuario": request.email
    })


# =========================
# HOME
# =========================
@app.route("/")
def home():
    return {"status": "SaaS rodando 🚀"}


# =========================
# START
# =========================
if __name__ == "__main__":
    app.run()
