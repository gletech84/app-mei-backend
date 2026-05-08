from flask import jsonify
from users.user_model import User

usuarios = []

def listar_usuarios():
    return jsonify({
        "total": len(usuarios),
        "usuarios": [u.__dict__ for u in usuarios]
    })