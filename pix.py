import requests

CLIENT_ID = "SUA_CLIENT_ID"
CLIENT_SECRET = "SUA_SECRET"
BASE_URL = "https://api.gerencianet.com.br"


def token():
    r = requests.post(
        f"{BASE_URL}/oauth/token",
        auth=(CLIENT_ID, CLIENT_SECRET),
        json={"grant_type": "client_credentials"}
    )
    return r.json()["access_token"]


def criar_pix(valor):
    t = token()

    headers = {"Authorization": f"Bearer {t}"}

    body = {
        "calendario": {"expiracao": 3600},
        "valor": {"original": valor},
        "chave": "SUA_CHAVE_PIX",
        "solicitacaoPagador": "Assinatura SaaS"
    }

    r = requests.post(
        f"{BASE_URL}/v2/cob",
        json=body,
        headers=headers
    )

    return r.json()
