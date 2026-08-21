import requests
import config_vpn


def criar_phase1(conexao):
    """
    Cria a Phase 1 (IKE Gateway) no FortiGate, definindo o peer remoto
    (Palo Alto) e a proposta de criptografia/hash/DH group.

    Nota: o FortiGate cria automaticamente a interface de túnel
    associada a esta Phase 1, com o mesmo nome - por isso a interface
    não é criada explicitamente antes deste passo.
    """
    url = f"{conexao['base_url']}/cmdb/vpn.ipsec/phase1-interface"
    proposta = config_vpn.PHASE1_PROPOSAL

    payload = {
        "name": config_vpn.TUNNEL_NAME,
        "interface": "port2",
        "ike-version": proposta["ike_version"],
        "remote-gw": config_vpn.PALOALTO_WAN_IP,
        "psksecret": config_vpn.IPSEC_PSK,
        "proposal": f"{proposta['encryption']}-{proposta['hash']}",
        "dhgrp": proposta["dh_group"],
        "keylife": proposta["lifetime_seconds"],
    }

    resposta = requests.post(url, headers=conexao["headers"], json=payload)
    return resposta


def configurar_ip_interface_tunel(conexao):
    """
    Atualiza (PUT) a interface de túnel - já criada automaticamente pelo
    FortiGate ao criar a Phase 1 - atribuindo o IP definido em
    config_vpn.FORTIGATE_TUNNEL_IP.
    """
    url = f"{conexao['base_url']}/cmdb/system/interface/{config_vpn.TUNNEL_NAME}"
    payload = {
        "ip": f"{config_vpn.FORTIGATE_TUNNEL_IP} 255.255.255.255",
        "remote-ip": f"{config_vpn.PALOALTO_TUNNEL_IP} 255.255.255.255",
    }

    resposta = requests.put(url, headers=conexao["headers"], json=payload)
    return resposta


def criar_phase2(conexao):
    """
    Cria a Phase 2 (IPSec Tunnel), associada à Phase 1 criada anteriormente,
    definindo a proposta de criptografia/autenticação e PFS.
    """
    url = f"{conexao['base_url']}/cmdb/vpn.ipsec/phase2-interface"
    proposta = config_vpn.PHASE2_PROPOSAL

    payload = {
        "name": config_vpn.TUNNEL_NAME,
        "phase1name": config_vpn.TUNNEL_NAME,
        "proposal": f"{proposta['encryption']}-{proposta['authentication']}",
        "pfs": "enable",
        "dhgrp": proposta["pfs_group"],
        "keylifeseconds": proposta["lifetime_seconds"],
        "src-subnet": "0.0.0.0 0.0.0.0",
        "dst-subnet": "0.0.0.0 0.0.0.0",
    }

    resposta = requests.post(url, headers=conexao["headers"], json=payload)
    return resposta


def criar_rota_estatica(conexao):
    """
    Cria a rota estática apontando o tráfego destinado à rede remota
    (Palo Alto) para a interface de túnel.
    """
    url = f"{conexao['base_url']}/cmdb/router/static"
    payload = {
        "dst": config_vpn.PALOALTO_LOCAL_NETWORK.replace("/", " ").split()[0] + " 255.255.255.0",
        "device": config_vpn.TUNNEL_NAME,
    }

    resposta = requests.post(url, headers=conexao["headers"], json=payload)
    return resposta


def criar_politica_firewall(conexao):
    """
    Cria as políticas de firewall permitindo tráfego bidirecional entre
    a LAN local (port1) e a interface de túnel.
    """
    url = f"{conexao['base_url']}/cmdb/firewall/policy"

    payload_saida = {
        "name": f"{config_vpn.TUNNEL_NAME}_OUT",
        "srcintf": [{"name": "port1"}],
        "dstintf": [{"name": config_vpn.TUNNEL_NAME}],
        "srcaddr": [{"name": "all"}],
        "dstaddr": [{"name": "all"}],
        "action": "accept",
        "schedule": "always",
        "service": [{"name": "ALL"}],
    }

    payload_entrada = {
        "name": f"{config_vpn.TUNNEL_NAME}_IN",
        "srcintf": [{"name": config_vpn.TUNNEL_NAME}],
        "dstintf": [{"name": "port1"}],
        "srcaddr": [{"name": "all"}],
        "dstaddr": [{"name": "all"}],
        "action": "accept",
        "schedule": "always",
        "service": [{"name": "ALL"}],
    }

    resposta_saida = requests.post(url, headers=conexao["headers"], json=payload_saida)
    resposta_entrada = requests.post(url, headers=conexao["headers"], json=payload_entrada)

    return resposta_saida, resposta_entrada


def configurar_vpn_completa(conexao):
    """
    Executa todos os passos, na ordem correta observada no comportamento
    real da API do FortiGate: Phase 1 (que cria a interface
    automaticamente) -> ajuste de IP da interface -> Phase 2 -> rota ->
    políticas.
    """
    resultados = {}

    resultados["phase1"] = criar_phase1(conexao).status_code
    resultados["ip_interface_tunel"] = configurar_ip_interface_tunel(conexao).status_code
    resultados["phase2"] = criar_phase2(conexao).status_code
    resultados["rota_estatica"] = criar_rota_estatica(conexao).status_code
    saida, entrada = criar_politica_firewall(conexao)
    resultados["politica_saida"] = saida.status_code
    resultados["politica_entrada"] = entrada.status_code

    return resultados