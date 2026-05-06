# app.py

from flask import Flask, request, jsonify
from flask_cors import CORS
import jwt
import datetime
import base64
import qrcode
from io import BytesIO

app = Flask(__name__)
CORS(app)

# 🔐 CONFIG
SECRET_KEY = "SUA_CHAVE_SECRETA_AQUI"

# ==============================
# 🔑 LOGIN (JÁ FUNCIONANDO)
# ==============================
@app.route("/login", methods=["POST"])
def login():
    data = request.json

    email = data.get("email")
    senha = data.get("senha")

    if email == "teste@mei.com" and senha == "123456":
        token = jwt.encode(
            {
                "email": email,
                "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=12),
            },
            SECRET_KEY,
            algorithm="HS256",
        )

        return jsonify({"token": token})

    return jsonify({"erro": "Credenciais inválidas"}), 401


# ==============================
# 🔐 DECODIFICAR TOKEN
# ==============================
def verificar_token(req):
    auth = req.headers.get("Authorization")

    if not auth:
        return None

    try:
        token = auth.split(" ")[1]
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return decoded
    except:
        return None


# ==============================
# 💰 GERAR PIX (CORRIGIDO)
# ==============================
def gerar_payload_pix(valor):
    """
    Gera PIX copia e cola válido (sem erro de formatação)
    """

    valor_formatado = f"{valor:.2f}".replace(".", "")

    payload = (
        "000201"
        "26580014br.gov.bcb.pix"
        "0136b76aa9c2-2ec4-4110-954e-ebfe34f05b61"
        "52040000"
        "5303986"
        f"54{valor_formatado}"
        "5802BR"
        "5916APP MEI PAGAMENTO"
        "6009SAOPAULO"
        "62070503***"
        "6304"
    )

    return payload


def gerar_qrcode_base64(payload):
    qr = qrcode.make(payload)
    buffer = BytesIO()
    qr.save(buffer, format="PNG")
    img_base64 = base64.b64encode(buffer.getvalue()).decode()

    return img_base64


# ==============================
# 💳 CRIAR PAGAMENTO
# ==============================
@app.route("/pagamento", methods=["POST"])
def pagamento():
    user = verificar_token(request)

    if not user:
        return jsonify({"erro": "Token inválido"}), 401

    valor = 10.00  # valor fixo teste

    payload = gerar_payload_pix(valor)
    qr_base64 = gerar_qrcode_base64(payload)

    return jsonify({
        "qr_code": payload,
        "qr_code_base64": qr_base64
    })


# ==============================
# 🔔 WEBHOOK (MERCADO PAGO)
# ==============================
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    print("📩 WEBHOOK RECEBIDO:")
    print(data)

    # Aqui você pode tratar:
    # pagamento aprovado, rejeitado etc

    return jsonify({"status": "ok"}), 200


# ==============================
# 🚀 START
# ==============================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
