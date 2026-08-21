import requests
import config_vpn


def conectar_fortigate():
    """
    Monta a URL base e os headers de autenticação (via API Token) para
    interagir com a API REST do FortiGate.

    Nota: usando HTTP (não HTTPS) porque a imagem de laboratório
    (FortiGate VM64-KVM sem licença) não expõe o serviço administrativo
    HTTPS corretamente - válido apenas para ambiente de teste isolado.
    Em um ambiente de produção real, HTTPS deveria ser sempre utilizado.
    """
    base_url = f"http://{config_vpn.FORTIGATE_HOST}/api/v2"
    headers = {
        "Authorization": f"Bearer {config_vpn.FORTIGATE_API_TOKEN}"
    }

    return {"base_url": base_url, "headers": headers}


def testar_conexao(conexao):
    """
    Faz uma chamada simples à API para confirmar que o token e a conexão
    estão funcionando corretamente. Consulta informações básicas do
    sistema (versão, hostname).
    """
    url = f"{conexao['base_url']}/cmdb/system/status"
    resposta = requests.get(url, headers=conexao["headers"])
    resposta.raise_for_status()

    return resposta.json()