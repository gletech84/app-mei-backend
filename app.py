# app.py

from flask import Flask, request, jsonify
import os
import base64
from io import BytesIO

import requests

# =========================================================
# CONFIG
# =========================================================

app = Flask(__name__)

MERCADO_PAGO_TOKEN = os.getenv("MP_ACCESS_TOKEN")

# =========================================================
# QR CODE (COM FALLBACK SE NÃO TIVER LIB)
# =========================================================

def gerar_qr_base64(texto):
    try:
        import qrcode

        qr = qrcode.make(texto)
        buffer = BytesIO()
        qr.save(buffer, format="PNG")

        return base64.b64encode(buffer.getvalue()).decode()

    except Exception as e:
        print("ERRO QRCode:", e)

        # fallback seguro (não quebra deploy)
        return ""

# =========================================================
# ROTA TESTE
# =========================================================

@app.route("/")
def home():
    return "API MEI ONLINE 🚀"

# =========================================================
# LOGIN (SIMPLES PRA TESTE)
# =========================================================

@app.route("/login", methods=["POST"])
def login():
    data = request.json

    if data.get("email") == "teste@mei.com":
        return jsonify({
            "token": "TOKEN_TESTE_123"
        })

    return jsonify({"erro": "Login inválido"}), 401

# =========================================================
# CRIAR PAGAMENTO PIX
# =========================================================

@app.route("/criar_pagamento", methods=["POST"])
def criar_pagamento():
    try:
        url = "https://api.mercadopago.com/v1/payments"

        headers = {
            "Authorization": f"Bearer {MERCADO_PAGO_TOKEN}",
            "Content-Type": "application/json"
        }

        body = {
            "transaction_amount": 10.00,
            "description": "Plano App MEI",
            "payment_method_id": "pix",
            "payer": {
                "email": "teste@mei.com"
            }
        }

        response = requests.post(url, json=body, headers=headers)

        if response.status_code != 201:
            print("ERRO MP:", response.text)
            return jsonify({"erro": "Erro ao criar pagamento"}), 500

        data = response.json()

        qr_code = data["point_of_interaction"]["transaction_data"]["qr_code"]

        qr_base64 = gerar_qr_base64(qr_code)

        return jsonify({
            "qr_code": qr_code,
            "qr_code_base64": qr_base64
        })

    except Exception as e:
        print("ERRO:", e)
        return jsonify({"erro": "Erro interno"}), 500

# =========================================================
# WEBHOOK MERCADO PAGO
# =========================================================

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.json
        print("WEBHOOK RECEBIDO:", data)

        # aqui você pode validar pagamento depois

        return "OK", 200

    except Exception as e:
        print("ERRO WEBHOOK:", e)
        return "Erro", 500

# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
