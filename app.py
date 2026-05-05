import os
import datetime
from flask import Flask, request, jsonify
import psycopg2
import jwt
from functools import wraps
import mercadopago

app = Flask(__name__)

# =========================
# CONFIG
# =========================
SECRET_KEY = os.getenv("SECRET_KEY", "dev_secret")
DATABASE_URL = os.getenv("DATABASE_URL")
MP_ACCESS_TOKEN = os.getenv("MP_ACCESS_TOKEN")

app.config["SECRET_KEY"] = SECRET_KEY

mp = mercadopago.SDK(MP_ACCESS_TOKEN)


# =========================
# DB
# =========================
def get_db():
    return psycopg2.connect(DATABASE_URL)


# =========================
# JWT
# =========================
def token_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):

        token = None

        if "Authorization" in request.headers:
            token = request.headers["Authorization"].split(" ")[1]

        if not token:
            return jsonify({"erro": "token ausente"}), 401

        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])

            user_id = data["user_id"]
            empresa_id = data["empresa_id"]
            plano = data.get("plano", "free")

        except:
            return jsonify({"erro": "token inválido"}), 401

        return f(user_id, empresa_id, plano, *args, **kwargs)

    return wrapper


# =========================
# CRIAR PAGAMENTO (MERCADO PAGO)
# =========================
@app.route("/pagamento", methods=["POST"])
@token_required
def criar_pagamento(user_id, empresa_id, plano):

    dados = request.json
    valor = float(dados.get("valor", 29.90))

    preference_data = {
        "items": [
            {
                "title": "Assinatura SaaS MEI PRO",
                "quantity": 1,
                "currency_id": "BRL",
                "unit_price": valor
            }
        ],
        "external_reference": str(empresa_id),
        "notification_url": "https://app-mei-backend.onrender.com/webhook"
    }

    preference_response = mp.preference().create(preference_data)

    init_point = preference_response["response"]["init_point"]

    return jsonify({
        "checkout_url": init_point
    })


# =========================
# WEBHOOK PAGAMENTO
# =========================
@app.route("/webhook", methods=["POST"])
def webhook():

    data = request.json

    try:
        payment_id = data["data"]["id"]
    except:
        return jsonify({"erro": "payload inválido"}), 400

    payment = mp.payment().get(payment_id)
    status = payment["response"]["status"]

    empresa_id = payment["response"]["external_reference"]

    if status == "approved":

        conn = get_db()
        cur = conn.cursor()

        # ativa assinatura por 30 dias
        expira = datetime.datetime.utcnow() + datetime.timedelta(days=30)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS assinaturas (
                id SERIAL PRIMARY KEY,
                empresa_id INTEGER,
                status TEXT,
                expira_em TIMESTAMP
            )
        """)

        cur.execute("""
            INSERT INTO assinaturas (empresa_id, status, expira_em)
            VALUES (%s, %s, %s)
        """, (empresa_id, "ativa", expira))

        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"status": "assinatura ativada"})

    return jsonify({"status": "pagamento não aprovado"})


# =========================
# DASHBOARD
# =========================
@app.route("/dashboard", methods=["GET"])
@token_required
def dashboard(user_id, empresa_id, plano):

    return jsonify({
        "status": "fase 8 SaaS real ativo",
        "plano": plano,
        "empresa": empresa_id
    })


# =========================
# HOME
# =========================
@app.route("/")
def home():
    return jsonify({
        "status": "saas fase 8 ativo",
        "nivel": "pagamento real integrado",
        "features": [
            "mercado pago",
            "webhook",
            "assinatura automática"
        ]
    })


# =========================
# RUN
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
