from backend.users.user_repository import criar_usuario, buscar_usuario

def registrar_ou_buscar(email):
    criar_usuario(email)
    return buscar_usuario(email)
