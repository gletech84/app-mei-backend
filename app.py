from flask import Flask, request, jsonify
import requests
import base64
from io import BytesIO
from PIL import Image

app = Flask(__name__)

# 🔐 TOKEN MERCADO PAGO (PRODUÇÃO)
ACCESS_TOKEN = "SEU_ACCESS_TOKEN_AQUI"

# =========================================
# 🔹 HEALTH CHECK
# =========================================
@app.route("/", methods=["GET"])
def home():
    return "API APP MEI ONLINE 🚀"


# =========================================
# 🔹 CRIAR PAGAMENTO PIX
# =========================================
@app.route("/criar-pagamento", methods=["POST"])
def criar_pagamento():
    try:
        data = request.json

        valor = data.get("valor", 10.0)
        descricao = data.get("descricao", "Pagamento App MEI")

        url = "https://api.mercadopago.com/v1/payments"

        headers = {
            "Authorization": f"Bearer {ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }

        body = {
            "transaction_amount": float(valor),
            "description": descricao,
            "payment_method_id": "pix",
            "payer": {
                "email": "cliente@teste.com"
            }
        }

        response = requests.post(url, json=body, headers=headers)

        if response.status_code not in [200, 201]:
            return jsonify({
                "erro": "Erro ao criar pagamento",
                "detalhes": response.text
            }), 400

        pagamento = response.json()

        # 🔹 QR Code texto (PIX copia e cola)
        qr_code = pagamento["point_of_interaction"]["transaction_data"]["qr_code"]

        # 🔹 Gerar imagem SEM biblioteca qrcode
        img = gerar_qr_base64(qr_code)

        return jsonify({
            "qr_code": qr_code,
            "qr_code_base64": img
        })

    except Exception as e:
        return jsonify({"erro": str(e)}), 500


# =========================================
# 🔹 GERAR QR BASE64 (SEM qrcode lib)
# =========================================
def gerar_qr_base64(texto):
    """
    Gera QR Code usando API externa (sem precisar instalar qrcode)
    """
    try:
        api_qr = "https://api.qrserver.com/v1/create-qr-code/"

        params = {
            "data": texto,
            "size": "300x300"
        }

        response = requests.get(api_qr, params=params)

        img = Image.open(BytesIO(response.content))

        buffer = BytesIO()
        img.save(buffer, format="PNG")

        return base64.b64encode(buffer.getvalue()).decode()

    except Exception as e:
        return ""


# =========================================
# 🔹 WEBHOOK MERCADO PAGO
# =========================================
@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.json

        print("📩 WEBHOOK RECEBIDO:")
        print(data)

        # 🔹 Aqui você pode tratar pagamento aprovado
        # exemplo:
        # if data["type"] == "payment":
        #     buscar pagamento e liberar acesso

        return jsonify({"status": "ok"}), 200

    except Exception as e:
        return jsonify({"erro": str(e)}), 500


# =========================================
# 🔹 RODAR APP
# =========================================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
