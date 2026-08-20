from panos.firewall import Firewall
import config_vpn


def conectar_paloalto():
    """
    Cria e retorna um objeto Firewall (pan-os-python) autenticado via
    API Key, representando a conexão com o Palo Alto.
    """
    firewall = Firewall(
        config_vpn.PALOALTO_HOST,
        api_key=config_vpn.PALOALTO_API_KEY,
    )

    return firewall


def testar_conexao(firewall):
    """
    Faz uma chamada simples para confirmar que a conexão e a API Key
    estão funcionando corretamente.
    """
    info = firewall.refresh_system_info()
    return info