import os
import datetime
from flask import Flask, request, jsonify
import psycopg2
import jwt
from functools import wraps

app = Flask(__name__)

# =========================
# CONFIG
# =========================
SECRET_KEY = os.getenv("SECRET_KEY", "dev_secret_key_change_me")
DATABASE_URL = os.getenv("DATABASE_URL")

app.config['SECRET_KEY'] = SECRET_KEY


# =========================
# DB CONNECTION
# =========================
def get_db():
    return psycopg2.connect(DATABASE_URL)


# =========================
# JWT DECORATOR
# =========================
def token_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):

        token = None

        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]

        if not token:
            return jsonify({"erro": "token ausente"}), 401

        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            user_id = data["user_id"]
            empresa_id = data["empresa_id"]
        except:
            return jsonify({"erro": "token inválido"}), 401

        return f(user_id, empresa_id, *args, **kwargs)

    return wrapper


# =========================
# LOGIN (gera empresa + user)
# =========================
@app.route("/login", methods=["POST"])
def login():

    data = request.json
    email = data.get("email")

    # SIMULAÇÃO SaaS (fase 5)
    empresa_id = 1
    user_id = 1

    token = jwt.encode({
        "user_id": user_id,
        "empresa_id": empresa_id,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }, SECRET_KEY, algorithm="HS256")

    return jsonify({
        "token": token,
        "empresa_id": empresa_id,
        "user_id": user_id
    })


# =========================
# DASHBOARD MULTI-EMPRESA
# =========================
@app.route("/dashboard", methods=["GET"])
@token_required
def dashboard(user_id, empresa_id):

    return jsonify({
        "status": "saas fase 5 ativo",
        "user_id": user_id,
        "empresa_id": empresa_id
    })


# =========================
# CRIAR EMPRESA (BASE SAAS)
# =========================
@app.route("/empresa", methods=["POST"])
@token_required
def criar_empresa(user_id, empresa_id):

    data = request.json
    nome = data.get("nome")

    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS empresas (
            id SERIAL PRIMARY KEY,
            nome TEXT,
            owner_id INTEGER
        )
    """)

    cur.execute(
        "INSERT INTO empresas (nome, owner_id) VALUES (%s, %s)",
        (nome, user_id)
    )

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"status": "empresa criada"})


# =========================
# EXEMPLO DADO POR EMPRESA
# =========================
@app.route("/dados", methods=["GET"])
@token_required
def dados(user_id, empresa_id):

    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS dados (
            id SERIAL PRIMARY KEY,
            empresa_id INTEGER,
            valor TEXT
        )
    """)

    cur.execute(
        "SELECT * FROM dados WHERE empresa_id = %s",
        (empresa_id,)
    )

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return jsonify({
        "empresa_id": empresa_id,
        "dados": rows
    })


# =========================
# HEALTH
# =========================
@app.route("/")
def home():
    return jsonify({
        "status": "saas backend online",
        "fase": 5
    })


# =========================
# RUN
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
