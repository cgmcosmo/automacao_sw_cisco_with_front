import requests
import config_vpn


def validar_fortigate(conexao):
    """
    Consulta o estado operacional real da VPN no FortiGate (não apenas
    a configuração), via API de monitoramento. Retorna se a Phase 1
    (IKE) e a Phase 2 (IPSec) estão efetivamente estabelecidas.
    """
    url = f"{conexao['base_url']}/monitor/vpn/ipsec"
    resposta = requests.get(url, headers=conexao["headers"])
    resposta.raise_for_status()
    dados = resposta.json()

    resultado = {
        "fabricante": "FortiGate",
        "ike_up": False,
        "ipsec_up": False,
        "detalhes": None,
    }

    for item in dados.get("results", []):
        if item.get("name") == config_vpn.TUNNEL_NAME:
            resultado["detalhes"] = item
            proxyids = item.get("proxyid", [])
            resultado["ipsec_up"] = any(p.get("status") == "up" for p in proxyids)
            resultado["ike_up"] = True

    return resultado


def validar_paloalto(firewall):
    """
    Consulta o estado operacional real da VPN no Palo Alto (não apenas
    a configuração), via comandos operacionais (op commands). Retorna
    se a IKE SA e a IPSec SA estão efetivamente estabelecidas.

    Nota: a resposta do comando "show vpn ike-sa" não inclui a palavra
    "Established" como texto puro (essa formatação só aparece na
    visualização em tabela do console) - a presença do nome do túnel
    configurado no XML de resposta já indica que a SA está ativa, já
    que SAs inativas ou expiradas não aparecem nesta consulta.
    """
    resultado = {
        "fabricante": "Palo Alto",
        "ike_up": False,
        "ipsec_up": False,
        "detalhes": None,
    }

    resposta_ike = firewall.op("show vpn ike-sa", cmd_xml=True)
    texto_ike = "" if resposta_ike is None else "".join(resposta_ike.itertext())

    if config_vpn.TUNNEL_NAME in texto_ike:
        resultado["ike_up"] = True

    resposta_ipsec = firewall.op("show vpn ipsec-sa", cmd_xml=True)
    texto_ipsec = "" if resposta_ipsec is None else "".join(resposta_ipsec.itertext())

    if config_vpn.TUNNEL_NAME in texto_ipsec:
        resultado["ipsec_up"] = True

    resultado["detalhes"] = {"ike_raw": texto_ike, "ipsec_raw": texto_ipsec}

    return resultado


def validar_vpn_completa(conexao_fortigate, firewall_paloalto):
    """
    Executa a validação operacional nos dois firewalls e consolida os
    resultados em uma lista de alertas, categorizados por severidade:
    - "critico": Phase 1 ou Phase 2 nao estabelecida em algum dos lados
    - "info": tudo estabelecido corretamente
    """
    resultado_forti = validar_fortigate(conexao_fortigate)
    resultado_pa = validar_paloalto(firewall_paloalto)

    alertas = []

    if not resultado_forti["ike_up"]:
        alertas.append({"severidade": "critico", "mensagem": "FortiGate: Phase 1 (IKE) nao estabelecida"})
    if not resultado_forti["ipsec_up"]:
        alertas.append({"severidade": "critico", "mensagem": "FortiGate: Phase 2 (IPSec) nao estabelecida"})

    if not resultado_pa["ike_up"]:
        alertas.append({"severidade": "critico", "mensagem": "Palo Alto: IKE SA nao estabelecida"})
    if not resultado_pa["ipsec_up"]:
        alertas.append({"severidade": "critico", "mensagem": "Palo Alto: IPSec SA nao estabelecida"})

    if not alertas:
        alertas.append({"severidade": "info", "mensagem": "VPN estabelecida corretamente em ambos os firewalls"})

    return {
        "fortigate": resultado_forti,
        "paloalto": resultado_pa,
        "alertas": alertas,
        "valido": all(a["severidade"] != "critico" for a in alertas),
    }