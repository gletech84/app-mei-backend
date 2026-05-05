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
SECRET_KEY = os.getenv("SECRET_KEY", "dev_secret")
DATABASE_URL = os.getenv("DATABASE_URL")

app.config["SECRET_KEY"] = SECRET_KEY


# =========================
# DB
# =========================
def get_db():
    return psycopg2.connect(DATABASE_URL)


# =========================
# JWT
# =========================
def token_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):

        token = None

        if "Authorization" in request.headers:
            token = request.headers["Authorization"].split(" ")[1]

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
# PLANO FREE LIMITS
# =========================
LIMITES_PLANO = {
    "free": 50,      # máximo 50 registros/dia
    "pro": 10000
}


# =========================
# LOGIN (SaaS base)
# =========================
@app.route("/login", methods=["POST"])
def login():

    data = request.json
    email = data.get("email")

    # SIMULAÇÃO SaaS
    user_id = 1
    empresa_id = 1
    plano = "free"

    token = jwt.encode({
        "user_id": user_id,
        "empresa_id": empresa_id,
        "plano": plano,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }, SECRET_KEY, algorithm="HS256")

    return jsonify({
        "token": token,
        "plano": plano
    })


# =========================
# DASHBOARD
# =========================
@app.route("/dashboard", methods=["GET"])
@token_required
def dashboard(user_id, empresa_id):

    return jsonify({
        "status": "fase 6 saas ativo",
        "empresa_id": empresa_id,
        "user_id": user_id
    })


# =========================
# CHECAR LIMITE DO PLANO
# =========================
def check_limit(plano, total_hoje):

    limite = LIMITES_PLANO.get(plano, 50)

    if total_hoje >= limite:
        return False

    return True


# =========================
# DADOS COM LIMITAÇÃO SAAS
# =========================
@app.route("/dados", methods=["POST"])
@token_required
def criar_dado(user_id, empresa_id):

    conn = get_db()
    cur = conn.cursor()

    plano = "free"  # depois vem do JWT real

    # contar registros hoje
    cur.execute("""
        SELECT COUNT(*) FROM dados
        WHERE empresa_id = %s
        AND DATE(created_at) = CURRENT_DATE
    """, (empresa_id,))

    total = cur.fetchone()[0]

    if not check_limit(plano, total):
        return jsonify({
            "erro": "limite do plano atingido",
            "plano": plano
        }), 403

    data = request.json
    valor = data.get("valor")

    cur.execute("""
        CREATE TABLE IF NOT EXISTS dados (
            id SERIAL PRIMARY KEY,
            empresa_id INTEGER,
            valor TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("""
        INSERT INTO dados (empresa_id, valor)
        VALUES (%s, %s)
    """, (empresa_id, valor))

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({
        "status": "registro criado",
        "plano": plano,
        "usados": total + 1
    })


# =========================
# STATUS SAAS
# =========================
@app.route("/")
def home():
    return jsonify({
        "status": "saas fase 6 ativo",
        "features": [
            "jwt",
            "multi-empresa",
            "limite por plano",
            "controle de uso"
        ]
    })


# =========================
# RUN LOCAL (IGNORADO NO RENDER)
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
