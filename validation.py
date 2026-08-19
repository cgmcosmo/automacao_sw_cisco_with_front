def validar_configuracao(conexao, vlans_esperadas, hostname_esperado):
    """
    Compara a configuração atual do switch com a configuração desejada
    (VLANs e hostname). Retorna um dicionário com o resultado da validação
    e uma lista de divergências encontradas (vazia se tudo estiver certo).
    """
    divergencias = []

    # --- Validação do hostname ---
    prompt_atual = conexao.find_prompt()
    # O prompt do Cisco vem como "NOME#" ou "NOME(config)#", removemos os símbolos
    hostname_atual = prompt_atual.replace("#", "").replace(">", "").strip()

    if hostname_atual != hostname_esperado:
        divergencias.append(
            f"Hostname divergente: esperado '{hostname_esperado}', encontrado '{hostname_atual}'"
        )

    # --- Validação das VLANs ---
    saida_vlans = conexao.send_command("show vlan brief")

    for vlan in vlans_esperadas:
        vlan_id = str(vlan["id"])
        vlan_name = vlan["name"]

        # Verifica se a linha da VLAN aparece na saída, com o nome correto
        linha_encontrada = False
        for linha in saida_vlans.splitlines():
            if linha.strip().startswith(vlan_id):
                linha_encontrada = True
                if vlan_name not in linha:
                    divergencias.append(
                        f"VLAN {vlan_id}: nome esperado '{vlan_name}', mas não encontrado na linha: '{linha.strip()}'"
                    )
                break

        if not linha_encontrada:
            divergencias.append(f"VLAN {vlan_id} ({vlan_name}) não foi encontrada no switch")

    resultado = {
        "valido": len(divergencias) == 0,
        "divergencias": divergencias,
    }

    return resultado