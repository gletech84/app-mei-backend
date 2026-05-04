# backend/payments.py
# STATUS: NOVO
# RESPONSABILIDADE: Webhook de pagamento SaaS

from fastapi import APIRouter, Request
from datetime import datetime, timedelta
import uuid

router = APIRouter()


# =========================
# WEBHOOK DE PAGAMENTO
# =========================
@router.post("/payment/webhook")
async def payment_webhook(request: Request):

    data = await request.json()

    """
    Estrutura esperada (Mercado Pago / Stripe):
    {
        "user_id": "...",
        "plan": "pro"
    }
    """

    user_id = data["user_id"]
    plan = data["plan"]

    # expiração padrão 30 dias
    expires = datetime.now() + timedelta(days=30)

    # salvar assinatura no banco
    # (exemplo simplificado - depois conecta Supabase)
    subscription = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "plan": plan,
        "status": "active",
        "expires_at": expires.isoformat()
    }

    return {
        "status": "activated",
        "subscription": subscription
    }