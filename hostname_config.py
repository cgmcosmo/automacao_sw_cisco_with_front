def configurar_hostname(conexao, hostname):
    """
    Altera o hostname do switch.
    Retorna a saída do comando aplicado.
    """
    comandos = [
        f"hostname {hostname}"
    ]

    saida = conexao.send_config_set(comandos)

    return saida