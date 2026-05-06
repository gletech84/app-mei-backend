from flask import session
from database import get_user

def login_user(email, senha):
    user = get_user(email, senha)

    if user:
        session["user_id"] = user[0]
        return True

    return False
