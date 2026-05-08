def verificar_acesso(usuario):
    """
    Regra central do SaaS:
    só libera acesso se assinatura estiver ativa
    """

    if not usuario:
        return False

    if usuario.get("plano") == "free":
        return False

    if usuario.get("assinatura_ativa") is False:
        return False

    return True