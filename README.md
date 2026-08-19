Automação de Switch Cisco com Frontend de Configuração

Projeto de automação em Python que se conecta via SSH a um switch Cisco (testado em laboratório EVE-NG) para configurar VLANs, alterar o hostname, salvar a configuração na NVRAM, gerar backups locais e validar se a configuração aplicada corresponde à configuração desejada.

Status do projeto
 Conexão SSH com o switch (Netmiko)
 Configuração de VLANs
 Configuração de hostname
 Salvamento da configuração na NVRAM
 Backup local da configuração (com hostname + data/hora no nome)
 Validação da configuração aplicada (VLANs + hostname)
 Frontend web (Flask) — em desenvolvimento
Tecnologias utilizadas
Python 3.12
Netmiko — automação de rede via SSH
Paramiko (<3.0) — necessário para compatibilidade com algoritmos de troca de chave (KEX) mais antigos, usados por imagens Cisco IOS de laboratório (EVE-NG)
Flask — frontend web (em desenvolvimento)
Ambiente de testes

O projeto foi desenvolvido e testado em um switch Cisco IOS simulado no EVE-NG, acessível via SSH.

Estrutura do projeto
automacao_sw_cisco_with_front/
├── config.py              # Configurações (IP, credenciais, VLANs, hostname alvo)
├── connection.py           # Conexão/desconexão SSH com o switch (Netmiko)
├── vlan_config.py          # Criação das VLANs no switch
├── hostname_config.py      # Alteração do hostname do switch
├── save_config.py          # Salva a configuração na NVRAM (write memory)
├── backup.py               # Backup local da configuração (com timestamp)
├── validation.py           # Validação da configuração aplicada vs esperada
├── backups/                # Arquivos de backup gerados (ignorados pelo Git)
├── teste_hostname.py       # Script de teste: configuração de hostname
├── teste_save.py           # Script de teste: salvamento na NVRAM
├── teste_backup.py         # Script de teste: backup de configuração
├── teste_validacao.py      # Script de teste: validação de configuração
├── requirements.txt        # Dependências do projeto
└── .gitignore
Configuração das VLANs

O script cria por padrão as seguintes VLANs:

ID	Nome
10	VLAN_DADOS
20	VLAN_VOZ
50	VLAN_SEGURANCA


Hostname aplicado

O script altera o hostname do switch para SWITCH_AUTOMATIZADO_R1 (valor predefinido em config.py).