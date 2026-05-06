from flask import Flask, request, jsonify

from users.user_service import registrar_ou_buscar
from auth.jwt import gerar_token
from billing.subscription_service import processar_pagamento
from webhooks.mercadopago_webhook import webhook

app = Flask(__name__)
app.register_blueprint(webhook)


@app.route("/")
def home():
    return jsonify({"status": "SAAS STARTUP FASE 11 ATIVO"})


@app.route("/login", methods=["POST"])
def login():
    email = request.json.get("email")

    user = registrar_ou_buscar(email)

    token = gerar_token(email)

    return jsonify({
        "token": token,
        "user": {
            "email": user[1],
            "plano": user[2],
            "assinatura": user[3]
        }
    })


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
