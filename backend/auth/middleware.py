from flask import request, jsonify
from auth.jwt import validar_token

def login_required(func):
    def wrapper(*args, **kwargs):
        token = request.headers.get("Authorization")

        if not token:
            return jsonify({"error": "token ausente"}), 401

        user_id = validar_token(token)

        if not user_id:
            return jsonify({"error": "token inválido"}), 401

        return func(user_id, *args, **kwargs)

    return wrapper