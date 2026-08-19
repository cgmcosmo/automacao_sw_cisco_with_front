from connection import conectar_switch, desconectar_switch
from validation import validar_configuracao
import config

conexao = conectar_switch()
resultado = validar_configuracao(conexao, config.VLANS, config.HOSTNAME_TARGET)

if resultado["valido"]:
    print("OK Configuração validada com sucesso! Tudo conforme esperado.")
else:
    print("ATENCÃO  Divergências encontradas na configuração:")
    for divergencia in resultado["divergencias"]:
        print(f"  - {divergencia}")

desconectar_switch(conexao)