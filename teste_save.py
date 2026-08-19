from connection import conectar_switch, desconectar_switch
from save_config import salvar_configuracao

conexao = conectar_switch()
resultado = salvar_configuracao(conexao)
print(resultado)
desconectar_switch(conexao)