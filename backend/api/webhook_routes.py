from fastapi import APIRouter

router = APIRouter()

@router.post("/mp")
def mercadopago_webhook():
    return {"message": "webhook recebido"}