import jwt
import datetime
import os

SECRET_KEY = os.getenv("SECRET_KEY", "default_secret")

def gerar_token(email):
    payload = {
        "email": email,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1)
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token
