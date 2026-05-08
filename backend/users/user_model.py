class User:
    def __init__(self, id, email):
        self.id = id
        self.email = email
        self.plano = "free"
        self.assinatura_ativa = False
        self.pagamento_status = "pending"