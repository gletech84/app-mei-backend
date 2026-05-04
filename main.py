# backend/main.py
# STATUS: NOVO
# RESPONSABILIDADE: API SaaS (autenticação + sync)

from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime

app = FastAPI()


# =========================
# MODELOS
# =========================
class LoginModel(BaseModel):
    email: str
    senha: str


class SyncModel(BaseModel):
    user_id: str
    payload: dict


# =========================
# BANCO SIMULADO (DEMO)
# =========================
USERS = {}
DATA = {}


# =========================
# LOGIN
# =========================
@app.post("/login")
def login(data: LoginModel):

    # MOCK simples (depois liga no DB real)
    if data.email == "admin" and data.senha == "123":
        return {
            "user_id": "1",
            "token": "token_demo",
            "status": "ok"
        }

    return {"error": "invalid login"}


# =========================
# SYNC UP (APP → CLOUD)
# =========================
@app.post("/sync/up")
def sync_up(data: SyncModel):

    DATA[data.user_id] = {
        "payload": data.payload,
        "updated_at": datetime.now()
    }

    return {
        "status": "synced",
        "timestamp": str(datetime.now())
    }


# =========================
# SYNC DOWN (CLOUD → APP)
# =========================
@app.get("/sync/down/{user_id}")
def sync_down(user_id: str):

    return DATA.get(user_id, {
        "status": "no_data"
    })