from flask import Blueprint, request, jsonify
from billing.subscription_service import processar_pagamento

webhook = Blueprint("webhook", __name__)

@webhook.route("/webhook", methods=["POST"])
def receber_webhook():
    data = request.json

    if data and data.get("type") == "payment":
        email = data.get("data", {}).get("payer", {}).get("email")

        if email:
            processar_pagamento(email)

    return jsonify({"status": "ok"})
