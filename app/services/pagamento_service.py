import mercadopago
import os

MP_ACCESS_TOKEN = os.getenv("MP_ACCESS_TOKEN")

sdk = mercadopago.SDK(MP_ACCESS_TOKEN)

def criar_pagamento(email):
    payment_data = {
        "transaction_amount": 19.90,
        "description": "Plano Premium MEI",
        "payment_method_id": "pix",
        "payer": {
            "email": email
        }
    }

    payment = sdk.payment().create(payment_data)
    return payment["response"]
