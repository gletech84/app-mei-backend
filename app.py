# app.py

from flask import Flask, request, jsonify
import requests
import base64
from io import BytesIO

# 🔥 QRCode (com fallback automático)
try:
    import qrcode
    QR_AVAILABLE = True
except ImportError:
    QR_AVAILABLE = False

app = Flask(__name__)

# 🔐 COLOQUE SEU TOKEN DE PRODUÇÃO AQUI
ACCESS_TOKEN = "SEU_ACCESS_TOKEN_AQUI"


# =========================
# HEALTH CHECK
# =========================
@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "online"}), 200


# =========================
# LOGIN (SIMPLES)
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

    try:
        response = requests.post(url, json=payload, headers=headers)

        # 🔥 TRATAMENTO SE NÃO FOR JSON
        try:
            mp_data = response.json()
        except Exception:
            return jsonify({
                "erro": "Resposta não é JSON",
                "status_code": response.status_code,
                "texto": response.text
            }), 500

        # 🔥 LOG COMPLETO (DEBUG)
        print("MP RESPONSE:", mp_data)

        # 🔥 VALIDAÇÃO DE ERRO DO MP
        if "error" in mp_data:
            return jsonify({
                "erro": "Erro do Mercado Pago",
                "detalhe": mp_data
            }), 400

        # 🔥 EXTRAÇÃO SEGURA
        try:
            qr_code = mp_data["point_of_interaction"]["transaction_data"]["qr_code"]
        except KeyError:
            return jsonify({
                "erro": "QR Code não encontrado",
                "resposta_mp": mp_data
            }), 500

        # 🔥 CORREÇÃO CRÍTICA
        qr_code = qr_code.replace(" ", "").replace("\n", "").strip()

        qr_base64 = None

        # 🔥 GERA IMAGEM SE LIB DISPONÍVEL
        if QR_AVAILABLE:
            try:
                qr = qrcode.make(qr_code)
                buffer = BytesIO()
                qr.save(buffer, format="PNG")
                qr_base64 = base64.b64encode(buffer.getvalue()).decode()
            except Exception as e:
                print("Erro ao gerar QR imagem:", e)

        return jsonify({
            "status": "ok",
            "qr_code": qr_code,
            "qr_code_base64": qr_base64
        }), 200

    except Exception as e:
        return jsonify({
            "erro": "Falha na requisição",
            "detalhe": str(e)
        }), 500


# =========================
# WEBHOOK (CONFIRMAÇÃO)
# =========================
@app.route("/webhook", methods=["POST"])
def webhook():

    try:
        data = request.json

        print("🔔 WEBHOOK RECEBIDO:")
        print(data)

        # 🔥 EXEMPLO DE TRATAMENTO
        if data and "type" in data:
            if data["type"] == "payment":
                print("💰 PAGAMENTO RECEBIDO")

        return jsonify({"status": "ok"}), 200

    except Exception as e:
        return jsonify({
            "erro": "Erro no webhook",
            "detalhe": str(e)
        }), 500


# =========================
# START APP
# =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
