from flask import Flask, request, jsonify

from users.user_service import registrar_ou_buscar
from auth.jwt import gerar_token
from billing.checkout import criar_checkout
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


@app.route("/checkout", methods=["POST"])
def checkout():
    email = request.json.get("email")
    plano = request.json.get("plano", "pro")

    link = criar_checkout(email, plano)

    return jsonify({"checkout": link})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
