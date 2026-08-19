def salvar_configuracao(conexao):
    """
    Salva a configuração atual (running-config) na NVRAM (startup-config),
    equivalente ao comando 'write memory' ou 'copy running-config startup-config'.
    Retorna a saída do comando.
    """
    saida = conexao.save_config()
    return saida