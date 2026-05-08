import mercadopago
import os

sdk = mercadopago.SDK(os.getenv("MP_ACCESS_TOKEN"))

def criar_pagamento(user_email):
    preference_data = {
        "items": [
            {
                "title": "Assinatura SaaS MEI",
                "quantity": 1,
                "unit_price": 29.90
            }
        ],
        "payer": {
            "email": user_email
        }
    }

    preference = sdk.preference().create(preference_data)
    return preference["response"]["init_point"]