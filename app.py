from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
API_SECRET = os.getenv("API_SECRET")


@app.route("/")
def home():
    return "Backend online"


# =========================
# WEBHOOK
# =========================
@app.route("/webhook", methods=["POST"])
def webhook():

    data = request.json

    if "data" not in data:
        return jsonify({"status": "ignored"})

    payment_id = data["data"]["id"]

    url = f"https://api.mercadopago.com/v1/payments/{payment_id}"

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}"
    }

    pagamento = requests.get(url, headers=headers).json()

    if pagamento["status"] == "approved":

        usuario_id = pagamento["metadata"]["usuario_id"]

        print(f"Pagamento aprovado para usuário {usuario_id}")

    return jsonify({"ok": True})


# =========================
# API SEGURA
# =========================
@app.route("/ativar-plano", methods=["POST"])
def ativar_plano():

    token = request.headers.get("Authorization")

    if token != f"Bearer {API_SECRET}":
        return jsonify({"erro": "não autorizado"}), 401

    data = request.json
    usuario_id = data.get("usuario_id")

    print(f"Ativar plano PRO para {usuario_id}")

    return jsonify({"status": "ok"})