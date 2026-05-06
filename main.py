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
# BANCO SIMULADO (TEMPORÁRIO)
# =========================
USERS = {}
DATA = {}


# =========================
# HEALTH CHECK (RENDER)
# =========================
@app.get("/")
def home():
    return {"status": "ok", "service": "saas-backend"}


# =========================
# LOGIN
# =========================
@app.post("/login")
def login(data: LoginModel):

    if data.email == "admin" and data.senha == "123":
        return {
            "user_id": "1",
            "token": "token_demo",
            "status": "ok"
        }

    return {"error": "invalid login"}


# =========================
# SYNC UP
# =========================
@app.post("/sync/up")
def sync_up(data: SyncModel):

    DATA[data.user_id] = {
        "payload": data.payload,
        "updated_at": datetime.utcnow().isoformat()
    }

    return {
        "status": "synced",
        "timestamp": datetime.utcnow().isoformat()
    }


# =========================
# SYNC DOWN
# =========================
@app.get("/sync/down/{user_id}")
def sync_down(user_id: str):

    return DATA.get(user_id, {
        "status": "no_data"
    })
