from flask import Flask, request, jsonify
import qrcode
import io
import base64

app = Flask(__name__)


# 🔹 Função para gerar QR Code em base64
def gerar_qr_code_pix(copia_cola: str):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(copia_cola)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    img_base64 = base64.b64encode(buffer.read()).decode("utf-8")

    return img_base64


# 🔹 Rota principal
@app.route("/")
def home():
    return jsonify({
        "status": "ok",
        "message": "API PIX rodando corretamente"
    })


# 🔹 Gerar PIX + QR Code
@app.route("/pix", methods=["POST"])
def criar_pix():
    data = request.json

    valor = data.get("valor", "10.00")
    nome = data.get("nome", "Cliente")

    # ⚠️ Aqui você pode substituir por integração real do banco
    copia_cola = (
        "00020126580014br.gov.bcb.pix0136EXEMPLO-PIX-CHAVE520400005303986540"
        + valor +
        "5802BR5913"
        + nome +
        "6009SAO PAULO62070503***6304"
    )

    qr_base64 = gerar_qr_code_pix(copia_cola)

    return jsonify({
        "qr_code": copia_cola,
        "qr_code_base64": qr_base64
    })


# 🔹 Execução local
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
