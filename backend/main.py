
from fastapi import FastAPI

from backend.routes import auth_routes

app = FastAPI(title="APP_MEI")

app.include_router(auth_routes.router)

@app.get("/")
def home():
    return {
        "status": "APP_MEI online",
        "version": "1.0"
app = FastAPI(title="APP_MEI")

# importa rotas organizadas
from backend.routes import users, auth

app.include_router(users.router)
app.include_router(auth.router)

@app.get("/")
def home():
    return {"status": "APP_MEI online", "version": "1.0"}
from fastapi import FastAPI

from backend.routes import auth_routes

app = FastAPI(title="APP_MEI")

app.include_router(auth_routes.router)

@app.get("/")
def home():
    return {
        "status": "APP_MEI online",
        "version": "1.0"
    }
