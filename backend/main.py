from fastapi import FastAPI

app = FastAPI(title="APP_MEI")

# importa rotas organizadas
from backend.routes import users, auth

app.include_router(users.router)
app.include_router(auth.router)

@app.get("/")
def home():
    return {"status": "APP_MEI online", "version": "1.0"}
