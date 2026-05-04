# backend/webhook_server.py
# STATUS: ATUALIZADO

from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

ACCESS_TOKEN = "SEU_TOKEN_MP"
API_SECRET = "SUA_CHAVE_SECRETA"


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

        # 🔐 chama sua API segura
        requests.post(
            "http://SEU_SERVIDOR:5001/ativar-plano",
            json={"usuario_id": usuario_id},
            headers={
                "Authorization": f"Bearer {API_SECRET}"
            }
        )

    return jsonify({"ok": True})