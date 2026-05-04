import os
from flask import Flask, jsonify
import psycopg2

app = Flask(__name__)

# =========================================
# CONFIG POSTGRES (RENDER)
# =========================================
DATABASE_URL = os.getenv("DATABASE_URL")


# =========================================
# HEALTH CHECK (Render usa isso)
# =========================================
@app.route("/")
def home():
    return jsonify({
        "status": "backend online",
        "sistema": "SaaS MEI backend",
        "database": "postgresql"
    })


# =========================================
# TESTE REAL DO BANCO POSTGRES
# =========================================
@app.route("/test-db")
def test_db():
    try:
        if not DATABASE_URL:
            return jsonify({
                "status": "erro",
                "message": "DATABASE_URL não configurada"
            }), 500

        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()

        cursor.execute("SELECT NOW();")
        time = cursor.fetchone()

        cursor.close()
        conn.close()

        return jsonify({
            "status": "ok",
            "message": "Conexão com PostgreSQL OK",
            "server_time": str(time[0])
        })

    except Exception as e:
        return jsonify({
            "status": "erro",
            "message": str(e)
        }), 500


# =========================================
# FUTURO SAAS (base pronta)
# =========================================
@app.route("/status")
def status():
    return jsonify({
        "saas": "fase 3 ativa",
        "arquitetura": "render + postgres + flask"
    })


# =========================================
# EXECUÇÃO LOCAL (IGNORADO NO RENDER)
# =========================================
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
