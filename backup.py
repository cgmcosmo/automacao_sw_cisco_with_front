from datetime import datetime
import os
import config


def fazer_backup(conexao, hostname):
    """
    Extrai a running-config do switch e salva num arquivo local dentro da pasta
    definida em config.BACKUP_DIR, nomeado com o hostname e a data/hora atual.
    Retorna o caminho do arquivo criado.
    """
    # Garante que a pasta de backups existe
    os.makedirs(config.BACKUP_DIR, exist_ok=True)

    # Pega a configuração completa (running-config) do switch
    conteudo_config = conexao.send_command("show running-config")

    # Monta o nome do arquivo: hostname + data/hora
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    nome_arquivo = f"{hostname}_{timestamp}.txt"
    caminho_arquivo = os.path.join(config.BACKUP_DIR, nome_arquivo)

    # Salva o conteúdo no arquivo
    with open(caminho_arquivo, "w") as arquivo:
        arquivo.write(conteudo_config)

    return caminho_arquivo