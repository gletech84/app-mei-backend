from flask import request, jsonify
import jwt
import os

SECRET_KEY = os.getenv("SECRET_KEY")

def token_required(f):
    def wrapper(*args, **kwargs):
        token = request.headers.get("Authorization")

        if not token:
            return jsonify({"erro": "Token ausente"}), 401

        try:
            token = token.split(" ")[1]
            jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        except:
            return jsonify({"erro": "Token inválido"}), 401

        return f(*args, **kwargs)

    return wrapper
