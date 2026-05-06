from flask import Flask, render_template, request, redirect, session, jsonify
from database import init_db, get_user
from pix import criar_pix
import sqlite3

app = Flask(__name__)
app.secret_key = "saas-secret-key"

init_db()


# ======================
# LOGIN
# ======================
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        senha = request.form["senha"]

        user = get_user(email, senha)

        if user:
            session["user_id"] = user[0]
            return redirect("/dashboard")

    return render_template("login.html")


# ======================
# DASHBOARD
# ======================
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/")

    conn = sqlite3.connect("saas.db")
    c = conn.cursor()

    c.execute("SELECT * FROM users WHERE id=?", (session["user_id"],))
    user = c.fetchone()

    return render_template("dashboard.html", user=user)


# ======================
# CHECKOUT PIX
# ======================
@app.route("/checkout")
def checkout():
    pix = criar_pix("10.00")
    return jsonify(pix)


# ======================
# WEBHOOK PIX
# ======================
@app.route("/webhook/pix", methods=["POST"])
def webhook():
    data = request.json

    txid = data.get("txid")
    status = data.get("status")

    conn = sqlite3.connect("saas.db")
    c = conn.cursor()

    if status == "CONCLUIDA":
        c.execute("UPDATE users SET ativo=1 WHERE id=1")

    conn.commit()
    conn.close()

    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
