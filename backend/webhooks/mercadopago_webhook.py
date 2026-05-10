from flask import Blueprint, request

from backend.billing.subscription_service import processar_pagamento


webhook = Blueprint("webhook", __name__)


@webhook.route("/webhook", methods=["POST"])
def receber_webhook():
    data = request.json

    if data.get("type") == "payment":
        email = data["data"].get("payer", {}).get("email")

        if email:
            processar_pagamento(email)

    return {"status": "ok"}
