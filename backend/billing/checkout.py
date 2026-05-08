import mercadopago
import os

sdk = mercadopago.SDK(os.getenv("MP_ACCESS_TOKEN"))

def criar_checkout(email, plano):
    preference_data = {
        "items": [
            {
                "title": f"Plano {plano}",
                "quantity": 1,
                "unit_price": 29.90
            }
        ],
        "payer": {
            "email": email
        }
    }

    preference = sdk.preference().create(preference_data)
    return preference["response"]["init_point"]