import requests

CLIENT_ID = "SUA_CLIENT_ID"
CLIENT_SECRET = "SUA_SECRET"
BASE_URL = "https://api.gerencianet.com.br"


def get_token():
    r = requests.post(
        f"{BASE_URL}/oauth/token",
        auth=(CLIENT_ID, CLIENT_SECRET),
        json={"grant_type": "client_credentials"}
    )
    return r.json()["access_token"]


def criar_pix(valor):
    token = get_token()

    headers = {"Authorization": f"Bearer {token}"}

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
