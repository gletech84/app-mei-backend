from auth.jwt import gerar_token

def login_usuario(email):
    token = gerar_token(email)

    return {
        "token": token,
        "tipo": "bearer"
    }