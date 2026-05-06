# app.py

from flask import Flask, request, jsonify
import requests
import base64
from io import BytesIO

# QR CODE (CORRETO)
import qrcode

app = Flask(__name__)

# 🔐 COLOQUE SEU TOKEN REAL AQUI (PRODUÇÃO)
ACCESS_TOKEN = "SEU_ACCESS_TOKEN_AQUI"


# =========================
# HEALTH CHECK
# =========================
@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "online"}), 200


# =========================
# GERAR PAGAMENTO PIX
# =========================
@app.route("/pagamento", methods=["POST"])
def pagamento():

    url = "https://api.mercadopago.com/v1/payments"

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "transaction_amount": 10,
        "description": "Assinatura App MEI",
        "payment_method_id": "pix",
        "payer": {
            "email": "cliente@teste.com",
            "first_name": "Cliente",
            "last_name": "Teste",
            "identification": {
                "type": "CPF",
                "number": "19119119100"
            }
        }
    }

    response = requests.post(url, json=payload, headers=headers)

    # =========================
    # TRATAMENTO DE RESPOSTA
    # =========================
    try:
        data = response.json()
    except Exception:
        return jsonify({
            "erro": "Resposta inválida do Mercado Pago",
            "texto": response.text
        }), 500

    if "error" in data:
        return jsonify({
            "erro": "Erro Mercado Pago",
            "detalhe": data
        }), 400

    # =========================
    # EXTRAI QR CODE
    # =========================
    try:
        qr_code = data["point_of_interaction"]["transaction_data"]["qr_code"]
    except KeyError:
        return jsonify({
            "erro": "QR Code não encontrado",
            "resposta": data
        }), 500

    # LIMPEZA
    qr_code = qr_code.replace(" ", "").replace("\n", "").strip()

    # =========================
    # GERA IMAGEM QR (BASE64)
    # =========================
    buffer = BytesIO()
    qr_img = qrcode.make(qr_code)
    qr_img.save(buffer, format="PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode()

    return jsonify({
        "status": "ok",
        "qr_code": qr_code,
        "qr_code_base64": qr_base64
    }), 200


# =========================
# WEBHOOK (CONFIRMAÇÃO)
# =========================
@app.route("/webhook", methods=["POST"])
def webhook():

    data = request.json
    print("WEBHOOK RECEBIDO:", data)

    return jsonify({"status": "ok"}), 200


# =========================
# START SERVER
# =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
