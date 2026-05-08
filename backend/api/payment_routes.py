from fastapi import APIRouter

router = APIRouter()

@router.get("/status")
def payment_status():
    return {"message": "payments OK"}