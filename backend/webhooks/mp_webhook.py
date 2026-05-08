from flask import Blueprint, request

webhook = Blueprint("webhook", __name__)

@webhook.route("/webhook", methods=["POST"])
def mp_webhook():
    data = request.json

    status = data.get("type")

    if status == "payment":
        # aqui você ativa assinatura
        print("Pagamento recebido")

    return {"status": "ok"}