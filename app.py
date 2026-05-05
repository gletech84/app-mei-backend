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
            plano = data.get("plano", "free")
            expira_em = data.get("expira_em")

        except:
            return jsonify({"erro": "token inválido"}), 401

        # =========================
        # BLOQUEIO POR EXPIRAÇÃO
        # =========================
        if expira_em:
            expira = datetime.datetime.fromisoformat(expira_em)

            if datetime.datetime.utcnow() > expira:
                return jsonify({
                    "erro": "assinatura expirada",
                    "acao": "upgrade_plano"
                }), 403

        return f(user_id, empresa_id, plano, *args, **kwargs)

    return wrapper


# =========================
# LOGIN (gera assinatura simulada)
# =========================
@app.route("/login", methods=["POST"])
def login():

    data = request.json
    email = data.get("email")

    user_id = 1
    empresa_id = 1

    plano = "free"

    expira_em = (datetime.datetime.utcnow() + datetime.timedelta(days=7)).isoformat()

    token = jwt.encode({
        "user_id": user_id,
        "empresa_id": empresa_id,
        "plano": plano,
        "expira_em": expira_em
    }, SECRET_KEY, algorithm="HS256")

    return jsonify({
        "token": token,
        "plano": plano,
        "expira_em": expira_em
    })


# =========================
# MIDDLEWARE SAAS CHECK
# =========================
def plano_liberado(plano):
    return plano in ["pro"]


# =========================
# DASHBOARD
# =========================
@app.route("/dashboard", methods=["GET"])
@token_required
def dashboard(user_id, empresa_id, plano):

    return jsonify({
        "status": "fase 7 saas real ativo",
        "empresa_id": empresa_id,
        "plano": plano
    })


# =========================
# DADOS COM BLOQUEIO DE PLANO
# =========================
@app.route("/dados", methods=["POST"])
@token_required
def criar_dado(user_id, empresa_id, plano):

    if plano == "free":
        return jsonify({
            "erro": "upgrade necessário",
            "plano_atual": plano,
            "acao": "assinar_pro"
        }), 403

    conn = get_db()
    cur = conn.cursor()

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
        "status": "criado com sucesso",
        "plano": plano
    })


# =========================
# UPGRADE PLANO (SIMULADO)
# =========================
@app.route("/upgrade", methods=["POST"])
@token_required
def upgrade(user_id, empresa_id, plano):

    novo_plano = "pro"

    expira_em = (datetime.datetime.utcnow() + datetime.timedelta(days=30)).isoformat()

    token = jwt.encode({
        "user_id": user_id,
        "empresa_id": empresa_id,
        "plano": novo_plano,
        "expira_em": expira_em
    }, SECRET_KEY, algorithm="HS256")

    return jsonify({
        "status": "upgrade realizado",
        "novo_plano": novo_plano,
        "token": token
    })


# =========================
# HEALTH CHECK
# =========================
@app.route("/")
def home():
    return jsonify({
        "status": "saas fase 7 ativo",
        "nivel": "monetizacao",
        "features": [
            "assinatura",
            "bloqueio de plano",
            "expiração",
            "upgrade"
        ]
    })


# =========================
# RUN
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
