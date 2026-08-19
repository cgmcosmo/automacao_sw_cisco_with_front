import warnings
warnings.filterwarnings("ignore")

from netmiko import ConnectHandler
import config

def conectar_switch():
    """
    Abre uma conexão SSH com o switch usando os dados do config.py.
    Retorna o objeto de conexão do Netmiko, que será usado para enviar comandos.
    """
    dispositivo = {
        "device_type": config.SWITCH_DEVICE_TYPE,
        "host": config.SWITCH_IP,
        "username": config.SWITCH_USERNAME,
        "password": config.SWITCH_PASSWORD,
        "secret": config.SWITCH_SECRET,
    }

    conexao = ConnectHandler(**dispositivo)

    # Entra no modo privilegiado (enable), necessário para configurar o switch
    conexao.enable()

    return conexao


def desconectar_switch(conexao):
    """
    Fecha a conexão SSH com o switch.
    """
    conexao.disconnect()