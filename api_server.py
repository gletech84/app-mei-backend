# backend/api_server.py
# STATUS: NOVO
# RESPONSABILIDADE: API segura para ativação de assinatura

from flask import Flask, request, jsonify

app = Flask(__name__)

API_SECRET = "SUA_CHAVE_SECRETA"


@app.route("/ativar-plano", methods=["POST"])
def ativar_plano():

    token = request.headers.get("Authorization")

    if token != f"Bearer {API_SECRET}":
        return jsonify({"erro": "não autorizado"}), 401

    data = request.json

    usuario_id = data.get("usuario_id")

    # 👉 aqui você chamaria o banco real
    print(f"ATIVAR PLANO PRO PARA {usuario_id}")

    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(port=5001)