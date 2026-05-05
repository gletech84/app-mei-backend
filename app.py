import os
from flask import Flask, jsonify
import psycopg2

app = Flask(__name__)

# =========================
# CONFIG POSTGRES
# =========================
DATABASE_URL = os.getenv("DATABASE_URL")

# =========================
# ROTA PRINCIPAL
# =========================
@app.route("/")
def home():
    return jsonify({
        "status": "backend online",
        "saas": "fase 3 ativo",
        "db": "postgresql"
    })

# =========================
# TESTE DO BANCO
# =========================
@app.route("/test-db")
def test_db():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()

        cursor.execute("SELECT NOW();")
        result = cursor.fetchone()

        cursor.close()
        conn.close()

        return jsonify({
            "status": "ok",
            "time": str(result[0])
        })

    except Exception as e:
        return jsonify({
            "status": "erro",
            "message": str(e)
        }), 500


# =========================
# START LOCAL
# =========================
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)        conn = psycopg2.connect(DATABASE_URL)
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
