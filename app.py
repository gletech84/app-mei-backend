import os
import psycopg2
import mercadopago
import jwt
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ==============================
# 🔐 CONFIGURAÇÕES
# ==============================

SECRET_KEY = os.getenv("SECRET_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")
MP_ACCESS_TOKEN = os.getenv("MP_ACCESS_TOKEN")

sdk = mercadopago.SDK(MP_ACCESS_TOKEN)

# ==============================
# 🗄️ CONEXÃO DB
# ==============================

def get_db():
    return psycopg2.connect(DATABASE_URL)

# ==============================
# 👤 REGISTRO
# ==============================

@app.route("/register", methods=["POST"])
def register():
    data = request.json
    email = data.get("email")
    senha = data.get("senha")

    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO users (email, senha, plano) VALUES (%s, %s, %s) RETURNING id",
        (email, senha, "free")
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

# ==============================
# 🔑 LOGIN
# ==============================

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    senha = data.get("senha")

    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        "SELECT id FROM users WHERE email=%s AND senha=%s",
        (email, senha)
    )

    user = cur.fetchone()

    cur.close()
    conn.close()

    if not user:
        return jsonify({"erro": "credenciais inválidas"}), 401

    token = jwt.encode(
        {
            "email": email,
            "exp": datetime.utcnow() + timedelta(hours=2)
        },
        SECRET_KEY,
        algorithm="HS256"
    )

    return jsonify({"token": token})

# ==============================
# 🔐 ROTA PROTEGIDA
# ==============================

@app.route("/protected", methods=["GET"])
def protected():
    auth_header = request.headers.get("Authorization")

    if not auth_header:
        return jsonify({"erro": "Token ausente"}), 401

    try:
        token = auth_header.split(" ")[1]
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        email = decoded["email"]

        return jsonify({
            "status": "acesso autorizado",
            "usuario": email
        })

    except Exception:
        return jsonify({"erro": "Token inválido"}), 401

# ==============================
# 💰 CRIAR PAGAMENTO PIX
# ==============================

@app.route("/criar_pagamento", methods=["POST"])
def criar_pagamento():
    data = request.json
    email = data.get("email")

    payment_data = {
        "transaction_amount": 10,
        "description": "Plano Premium MEI",
        "payment_method_id": "pix",
        "payer": {
            "email": email
        }
    }

    payment = sdk.payment().create(payment_data)
    response = payment["response"]

    pix_data = response["point_of_interaction"]["transaction_data"]

    # 🔥 CORREÇÃO DO BUG DO PIX (SEM ESPAÇO)
    qr_code = pix_data["qr_code"].replace(" ", "").strip()

    return jsonify({
        "qr_code": qr_code,
        "qr_code_base64": pix_data["qr_code_base64"]
    })

# ==============================
# 🔔 WEBHOOK MERCADO PAGO
# ==============================

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    if data.get("type") == "payment":
        payment_id = data["data"]["id"]

        payment = sdk.payment().get(payment_id)
        response = payment["response"]

        if response["status"] == "approved":
            email = response["payer"]["email"]

            conn = get_db()
            cur = conn.cursor()

            cur.execute(
                "UPDATE users SET plano='premium' WHERE email=%s",
                (email,)
            )

            conn.commit()
            cur.close()
            conn.close()

    return jsonify({"status": "ok"})

# ==============================
# 🚀 START
# ==============================

if __name__ == "__main__":
    app.run(debug=True)
