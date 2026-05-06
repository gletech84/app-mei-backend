# app.py

from flask import Flask, request, jsonify
import requests
import base64
import qrcode
from io import BytesIO

app = Flask(__name__)

# 🔐 TOKEN MERCADO PAGO (COLOQUE O SEU)
ACCESS_TOKEN = "SEU_ACCESS_TOKEN_AQUI"

# =========================
# LOGIN (TESTE)
# =========================
@app.route("/login", methods=["POST"])
def login():
    return jsonify({
        "token": "fake-jwt-token"
    })


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

    data = {
        "transaction_amount": 10,
        "description": "Assinatura App MEI",
        "payment_method_id": "pix",
        "payer": {
            "email": "teste@mei.com"
        }
    }

    response = requests.post(url, json=data, headers=headers)
    mp_data = response.json()

    try:
        # 🔥 PEGA O PIX
        qr_code = mp_data["point_of_interaction"]["transaction_data"]["qr_code"]

        # 🔥 CORREÇÃO CRÍTICA (REMOVE ESPAÇOS)
        qr_code = qr_code.replace(" ", "").strip()

        # 🔥 GERA IMAGEM QR CODE
        qr = qrcode.make(qr_code)
        buffer = BytesIO()
        qr.save(buffer, format="PNG")
        qr_base64 = base64.b64encode(buffer.getvalue()).decode()

        return jsonify({
            "qr_code": qr_code,
            "qr_code_base64": qr_base64
        })

    except Exception as e:
        return jsonify({
            "erro": "Erro ao gerar PIX",
            "detalhe": str(e),
            "resposta_mp": mp_data
        }), 500


# =========================
# WEBHOOK (OBRIGATÓRIO)
# =========================
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    print("🔔 WEBHOOK RECEBIDO:", data)

    return jsonify({"status": "ok"}), 200


# =========================
# START
# =========================
if __name__ == "__main__":
    app.run(debug=True)
