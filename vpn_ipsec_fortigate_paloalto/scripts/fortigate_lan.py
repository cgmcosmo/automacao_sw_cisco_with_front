import requests
import config_vpn


def configurar_lan(conexao):
    """
    Configura a interface LAN (port1) do FortiGate:
    - Define o modo como estático (static) e atribui o IP do gateway
      da rede local do FortiGate.

    Nota: por padrão a interface port1 estava em modo DHCP - é
    necessário definir explicitamente mode="static" para que o campo
    "ip" seja de fato aplicado (com mode=dhcp, o FortiGate ignora
    qualquer IP estático enviado no payload).
    """
    resultados = {}

    rede, prefixo = config_vpn.FORTIGATE_LOCAL_NETWORK.split("/")
    octetos = rede.split(".")
    octetos[-1] = "1"
    ip_gateway = ".".join(octetos)

    try:
        url = f"{conexao['base_url']}/cmdb/system/interface/port1"
        payload = {
            "mode": "static",
            "ip": f"{ip_gateway} 255.255.255.0",
            "allowaccess": "ping",
        }
        resposta = requests.put(url, headers=conexao["headers"], json=payload)
        resposta.raise_for_status()
        resultados["interface_lan"] = "OK"
    except Exception as erro:
        resultados["interface_lan"] = f"ERRO: {erro}"

    return resultados