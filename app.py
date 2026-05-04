from flask import Flask, request, jsonify
import os
import requests

app = Flask(__name__)

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
API_SECRET = os.getenv("API_SECRET")


# =========================
# HEALTH CHECK
# =========================
@app.route("/")
def home():
    return jsonify({"status": "backend online"})


# =========================
# WEBHOOK MERCADO PAGO
# =========================
@app.route("/webhook", methods=["POST"])
def webhook():

    data = request.json

    if not data or "data" not in data:
        return jsonify({"status": "ignored"})

    payment_id = data["data"]["id"]

    url = f"https://api.mercadopago.com/v1/payments/{payment_id}"

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}"
    }

    pagamento = requests.get(url, headers=headers).json()

    if pagamento.get("status") == "approved":

        usuario_id = pagamento.get("metadata", {}).get("usuario_id")

        print(f"✅ PAGAMENTO APROVADO: {usuario_id}")

        # aqui você ativa o plano no banco depois
        # ex: SubscriptionService.ativar(usuario_id)

    return jsonify({"ok": True})


# =========================
# ATIVAÇÃO DE PLANO (SEGURA)
# =========================
@app.route("/ativar-plano", methods=["POST"])
def ativar_plano():

    token = request.headers.get("Authorization")

    if token != f"Bearer {API_SECRET}":
        return jsonify({"erro": "não autorizado"}), 401

    data = request.json
    usuario_id = data.get("usuario_id")

    print(f"🚀 Plano PRO ativado para: {usuario_id}")

    return jsonify({"status": "ok", "plano": "pro"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)