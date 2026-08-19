from connection import conectar_switch, desconectar_switch
from hostname_config import configurar_hostname
import config

conexao = conectar_switch()
resultado = configurar_hostname(conexao, config.HOSTNAME_TARGET)
print(resultado)
desconectar_switch(conexao)