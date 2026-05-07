from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class LoginModel(BaseModel):
    email: str
    senha: str


@router.post("/login")
def login(data: LoginModel):

    if data.email == "admin" and data.senha == "123":
        return {
            "user_id": "1",
            "token": "token_demo",
            "status": "ok"
        }

    return {"error": "invalid login"}
