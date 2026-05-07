from fastapi import FastAPI

app = FastAPI(title="APP_MEI API", version="1.0")

@app.get("/")
def home():
    return {
        "status": "ok",
        "message": "APP_MEI rodando com sucesso"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }
