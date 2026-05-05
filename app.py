import os
from flask import Flask, jsonify
import psycopg2

app = Flask(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")


@app.route("/")
def home():
    return jsonify({
        "status": "backend online",
        "saas": "fase 3 ativo",
        "versao": "1.0"
    })


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
            "hora_servidor": str(result[0])
        })

    except Exception as e:
        return jsonify({
            "status": "erro",
            "message": str(e)
        }), 500


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
