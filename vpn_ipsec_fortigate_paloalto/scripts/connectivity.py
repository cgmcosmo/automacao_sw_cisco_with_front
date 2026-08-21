import re
from netmiko import ConnectHandler
import config_vpn


def testar_conectividade(destino=None, count=4):
    """
    Dispara um ping a partir do FortiGate (via CLI, usando Netmiko),
    em direção à rede remota (atrás do Palo Alto), simulando o tráfego
    real de produção que atravessaria o túnel IPSec.

    Por padrão, testa o IP do host de teste na LAN remota (VPC5,
    10.20.20.2).

    Nota: a API REST do FortiGate nesta versão (v7.0.9) não expõe um
    endpoint de execução de ping - por isso este teste usa SSH/CLI
    (execute ping), a mesma abordagem já validada na Parte 1 deste
    desafio.
    """
    if destino is None:
        destino = "10.20.20.2"

    dispositivo = {
        "device_type": "fortinet",
        "host": config_vpn.FORTIGATE_HOST,
        "username": config_vpn.FORTIGATE_SSH_USERNAME,
        "password": config_vpn.FORTIGATE_SSH_PASSWORD,
        "use_keys": False,
    }

    conexao = ConnectHandler(**dispositivo)
    saida = conexao.send_command(f"execute ping {destino}", read_timeout=15)
    conexao.disconnect()

    # Extrai o percentual exato de perda de pacotes (evita falso positivo,
    # já que "100% packet loss" contém a substring "0% packet loss")
    match = re.search(r"(\d+)%\s*packet loss", saida)
    sucesso = match is not None and int(match.group(1)) < 100

    resultado = {
        "destino": destino,
        "sucesso": sucesso,
        "saida_bruta": saida,
    }

    return resultado


def testar_conectividade_completa(destino=None):
    """
    Executa o teste de conectividade e retorna um relatório com
    interpretação clara do resultado.
    """
    resultado = testar_conectividade(destino)

    if resultado["sucesso"]:
        mensagem = f"Conectividade OK: {resultado['destino']} respondeu ao ping"
        severidade = "info"
    else:
        mensagem = f"Falha de conectividade: {resultado['destino']} nao respondeu ao ping"
        severidade = "critico"

    return {
        "resultado": resultado,
        "mensagem": mensagem,
        "severidade": severidade,
    }