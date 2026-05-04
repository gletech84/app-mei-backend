# backend/mercadopago_webhook.py
# STATUS: NOVO
# RESPONSABILIDADE: Ativar assinatura via Mercado Pago

from fastapi import APIRouter, Request
from datetime import datetime, timedelta
import uuid

router = APIRouter()


# =========================
# WEBHOOK MERCADO PAGO
# =========================
@router.post("/mp/webhook")
async def mercadopago_webhook(request: Request):

    data = await request.json()

    """
    Esperado do Mercado Pago:
    {
        "user_id": "...",
        "plan": "pro",
        "status": "approved"
    }
    """

    if data.get("status") != "approved":
        return {"status": "ignored"}

    user_id = data["user_id"]
    plan = data["plan"]

    expires_at = datetime.now() + timedelta(days=30)

    subscription = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "plan": plan,
        "status": "active",
        "expires_at": expires_at.isoformat(),
        "created_at": datetime.now().isoformat()
    }

    # Aqui você salva no Supabase
    # (pseudo-call REST ou SDK)
    print("[SUBSCRIPTION ACTIVATED]", subscription)

    return {
        "status": "activated",
        "subscription": subscription
    }