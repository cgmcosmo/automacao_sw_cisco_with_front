from connection import conectar_switch, desconectar_switch
from backup import fazer_backup
import config

conexao = conectar_switch()
caminho = fazer_backup(conexao, config.HOSTNAME_TARGET)
print(f"Backup salvo em: {caminho}")
desconectar_switch(conexao)