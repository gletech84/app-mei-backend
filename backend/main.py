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
