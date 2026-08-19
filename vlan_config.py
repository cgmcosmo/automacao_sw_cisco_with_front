def configurar_vlans(conexao, vlans):
    """
    Cria as VLANs no switch com base numa lista de dicionários {"id": ..., "name": ...}.
    """
    comandos = []

    for vlan in vlans:
        comandos.append(f"vlan {vlan['id']}")
        comandos.append(f"name {vlan['name']}")

    # send_config_set entra automaticamente no modo "configure terminal",
    # envia os comandos linha a linha, e sai no final
    saida = conexao.send_config_set(comandos)

    return saida