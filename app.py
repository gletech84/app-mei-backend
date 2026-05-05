import os
import datetime
from flask import Flask, request, jsonify
import psycopg2
import jwt
from functools import wraps

app = Flask(__name__)

# =========================
# CONFIGURAÇÕES JWT
# =========================
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "dev_secret_key_change_me")

DATABASE_URL = os.getenv("DATABASE_URL")

# =========================
# CONEXÃO BANCO
# =========================
def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL)
    return conn

# =========================
# DECORATOR JWT (PROTEÇÃO)
# =========================
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]

        if not token:
            return jsonify({"erro": "Token ausente"}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = data['user']
        except:
            return jsonify({"erro": "Token inválido"}), 401

        return f(current_user, *args, **kwargs)

    return decorated

# =========================
# LOGIN (GERA JWT)
# =========================
@app.route('/login', methods=['POST'])
def login():
    data = request.json

    username = data.get("username")
    password = data.get("password")

    if username == "admin" and password == "123":
        token = jwt.encode({
            "user": username,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }, app.config['SECRET_KEY'], algorithm="HS256")

        return jsonify({"token": token})

    return jsonify({"erro": "credenciais inválidas"}), 401

# =========================
# ROTA PROTEGIDA
# =========================
@app.route('/dashboard', methods=['GET'])
@token_required
def dashboard(current_user):
    return jsonify({
        "status": "ok",
        "user": current_user,
        "saas": "fase 4 JWT ativo"
    })

# =========================
# HEALTH CHECK
# =========================
@app.route('/')
def home():
    return jsonify({
        "status": "backend online",
        "versao": "1.1",
        "jwt": "ativo"
    })

# =========================
# START SERVER
# =========================
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
