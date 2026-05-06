# app.py

from flask import Flask, request, jsonify
import requests
import base64
from io import BytesIO

# IMPORT CORRETO (SEM TRADUÇÃO)
try:
    import qrcode
    QR_AVAILABLE = True
except ImportError:
    QR_AVAILABLE = False

app = Flask(__name__)

ACCESS_TOKEN = "SEU_ACCESS_TOKEN_AQUI"


@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "online"}), 200


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

    try:
        data = response.json()
    except:
        return jsonify({
            "erro": "Resposta inválida",
            "texto": response.text
        }), 500

    if "error" in data:
        return jsonify(data), 400

    qr_code = data["point_of_interaction"]["transaction_data"]["qr_code"]

    # 🔥 LIMPEZA CRÍTICA
    qr_code = qr_code.replace(" ", "").replace("\n", "").strip()

    qr_base64 = None

    if QR_AVAILABLE:
        qr = qrcode.make(qr_code)
        buffer = BytesIO()
        qr.save(buffer, format="PNG")
        qr_base64 = base64.b64encode(buffer.getvalue()).decode()

    return jsonify({
        "qr_code": qr_code,
        "qr_code_base64": qr_base64
    })


@app.route("/webhook", methods=["POST"])
def webhook():
    print("WEBHOOK:", request.json)
    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
