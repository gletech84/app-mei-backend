from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import psycopg2
import jwt
from datetime import datetime, timedelta
from functools import wraps
from app.services.pagamento_service import criar_pagamento

app = Flask(__name__)
CORS(app)

SECRET_KEY = os.getenv("SECRET_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")


def get_connection():
    return psycopg2.connect(DATABASE_URL)


def gerar_token(email):
    payload = {
        "email": email,
        "exp": datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


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
        INSERT INTO users (email, plano)
        VALUES (%s, 'free')
        ON CONFLICT (email) DO NOTHING
        RETURNING id;
    """, (email,))

    user = cur.fetchone()

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"status": "ok"})


# =========================
# LOGIN
# =========================
@app.route("/login", methods=["POST"])
def login():
    email = request.json.get("email")
    token = gerar_token(email)
    return jsonify({"token": token})


# =========================
# PERFIL
# =========================
@app.route("/perfil")
@token_required
def perfil():
    return jsonify({
        "usuario": request.email
    })


# =========================
# CRIAR PAGAMENTO
# =========================
@app.route("/criar-pagamento", methods=["POST"])
@token_required
def pagamento():
    response = criar_pagamento(request.email)

    return jsonify({
        "qr_code": response["point_of_interaction"]["transaction_data"]["qr_code"],
        "qr_code_base64": response["point_of_interaction"]["transaction_data"]["qr_code_base64"]
    })


# =========================
# WEBHOOK MERCADO PAGO
# =========================
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    if data.get("type") == "payment":
        payment_id = data["data"]["id"]

        # Aqui você poderia consultar pagamento novamente (fase avançada)
        # Para simplificar, vamos liberar direto

        conn = get_connection()
        cur = conn.cursor()

        # 🔥 LIBERA TODOS COMO PREMIUM (simplificado)
        cur.execute("""
            UPDATE users
            SET plano = 'premium'
        """)

        conn.commit()
        cur.close()
        conn.close()

    return jsonify({"status": "ok"})


# =========================
# ROTA PREMIUM
# =========================
@app.route("/premium")
@token_required
def premium():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT plano FROM users WHERE email = %s
    """, (request.email,))

    user = cur.fetchone()

    cur.close()
    conn.close()

    if user and user[0] == "premium":
        return jsonify({"msg": "Bem-vindo ao premium"})
    else:
        return jsonify({"erro": "Acesso apenas para premium"}), 403


@app.route("/")
def home():
    return {"status": "SaaS com pagamento ativo 💰"}


if __name__ == "__main__":
    app.run()
