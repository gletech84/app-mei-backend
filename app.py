from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
import jwt
import datetime
import os
import mercadopago

app = Flask(__name__)
CORS(app)

# =========================
# CONFIG
# =========================
SECRET_KEY = os.getenv("SECRET_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")
MP_ACCESS_TOKEN = os.getenv("MP_ACCESS_TOKEN")


# =========================
# CONEXÃO BANCO
# =========================
def get_connection():
    return psycopg2.connect(DATABASE_URL)


# =========================
# HOME
# =========================
@app.route("/")
def home():
    return {"status": "API ONLINE 🚀"}


# =========================
# REGISTER
# =========================
@app.route("/register", methods=["POST"])
def register():
    data = request.json
    email = data.get("email")

    if not email:
        return jsonify({"erro": "Email obrigatório"}), 400

    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO users (email, plano)
            VALUES (%s, 'free')
            RETURNING id;
        """, (email,))

        user_id = cur.fetchone()[0]

        conn.commit()
        cur.close()
        conn.close()

        return jsonify({
            "status": "usuário criado",
            "user_id": user_id,
            "email": email
        })

    except Exception as e:
        return jsonify({"erro": str(e)}), 500


# =========================
# LOGIN
# =========================
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")

    if not email:
        return jsonify({"erro": "Email obrigatório"}), 400

    payload = {
        "email": email,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    if isinstance(token, bytes):
        token = token.decode("utf-8")

    return jsonify({"token": token})


# =========================
# ROTA PROTEGIDA
# =========================
@app.route("/protegido", methods=["GET"])
def protegido():
    auth_header = request.headers.get("Authorization")

    if not auth_header:
        return jsonify({"erro": "Token ausente"}), 401

    try:
        token = auth_header.replace("Bearer ", "")
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])

        return jsonify({
            "status": "acesso autorizado",
            "usuario": decoded["email"]
        })

    except Exception:
        return jsonify({"erro": "Token inválido"}), 401


# =========================
# CRIAR PAGAMENTO PIX
# =========================
@app.route("/criar-pagamento", methods=["POST"])
def criar_pagamento():
    try:
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return jsonify({"erro": "Token ausente"}), 401

        token = auth_header.replace("Bearer ", "")
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        email = decoded["email"]

        sdk = mercadopago.SDK(MP_ACCESS_TOKEN)

        payment_data = {
            "transaction_amount": 10,
            "description": "Plano Premium",
            "payment_method_id": "pix",
            "payer": {
                "email": email
            }
        }

        payment = sdk.payment().create(payment_data)
        response = payment["response"]

        qr_code = response["point_of_interaction"]["transaction_data"]["qr_code"]
        qr_code_base64 = response["point_of_interaction"]["transaction_data"]["qr_code_base64"]

        return jsonify({
            "qr_code": qr_code,
            "qr_code_base64": qr_code_base64
        })

    except Exception as e:
        return jsonify({"erro": str(e)}), 500


# =========================
# WEBHOOK MERCADO PAGO
# =========================
@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.json

        if not data:
            return jsonify({"status": "sem dados"}), 200

        # Mercado Pago envia tipo notification
        if data.get("type") != "payment":
            return jsonify({"status": "ignorado"}), 200

        payment_id = data["data"]["id"]

        sdk = mercadopago.SDK(MP_ACCESS_TOKEN)
        payment = sdk.payment().get(payment_id)

        response = payment["response"]

        status = response.get("status")
        email = response.get("payer", {}).get("email")

        # 🔥 SÓ LIBERA SE PAGAMENTO APROVADO
        if status == "approved" and email:

            conn = get_connection()
            cur = conn.cursor()

            cur.execute("""
                UPDATE users
                SET plano = 'premium'
                WHERE email = %s;
            """, (email,))

            conn.commit()
            cur.close()
            conn.close()

            return jsonify({
                "status": "usuário atualizado para premium",
                "email": email
            })

        return jsonify({"status": "pagamento não aprovado"}), 200

    except Exception as e:
        return jsonify({"erro": str(e)}), 500


# =========================
# START
# =========================
if __name__ == "__main__":
    app.run(debug=True)
