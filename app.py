from flask import Flask, request, jsonify
import sqlite3
from database import init_db
from pix_service import criar_cobranca

app = Flask(__name__)

init_db()


# =========================
# 🧑 CRIAR USUÁRIO
# =========================
@app.route("/register", methods=["POST"])
def register():
    data = request.json

    conn = sqlite3.connect("saas.db")
    c = conn.cursor()

    c.execute(
        "INSERT INTO users (email, senha, plano) VALUES (?, ?, ?)",
        (data["email"], data["senha"], data.get("plano", "basico"))
    )

    conn.commit()
    conn.close()

    return jsonify({"status": "usuario criado"})


# =========================
# 💰 GERAR PIX
# =========================
@app.route("/checkout", methods=["POST"])
def checkout():
    data = request.json

    valor = data.get("valor", "10.00")

    pix = criar_cobranca(valor, "SUA_CHAVE_PIX")

    return jsonify(pix)


# =========================
# 🔔 WEBHOOK PIX
# =========================
@app.route("/webhook/pix", methods=["POST"])
def webhook():
    data = request.json

    txid = data.get("txid")
    status = data.get("status")

    conn = sqlite3.connect("saas.db")
    c = conn.cursor()

    c.execute("INSERT INTO pagamentos (txid, status, user_id) VALUES (?, ?, ?)",
              (txid, status, 1))

    if status == "CONCLUIDA":
        c.execute("UPDATE users SET ativo = 1 WHERE id = 1")

    conn.commit()
    conn.close()

    return jsonify({"ok": True})


# =========================
# 🌐 STATUS
# =========================
@app.route("/")
def home():
    return jsonify({"status": "SAAS PIX ONLINE"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
