# Automação de Switch Cisco com Frontend de Configuração

Projeto de automação em Python que se conecta via SSH a um switch Cisco
(testado em laboratório EVE-NG) para configurar VLANs, alterar o hostname,
salvar a configuração na NVRAM, gerar backups locais e validar se a
configuração aplicada corresponde à configuração desejada — tudo através
de um frontend web feito em Flask.

## Vídeo de demonstração

Um vídeo com o funcionamento completo do projeto (formulário, aplicação
da configuração, validação, salvamento na NVRAM e detecção de
divergência) está disponível em [`evidencias/demo_funcionamento.mp4`](evidencias/demo_funcionamento.mp4).

## Status do projeto

- [x] Conexão SSH com o switch (Netmiko)
- [x] Configuração de VLANs
- [x] Configuração de hostname
- [x] Salvamento da configuração na NVRAM (controlado pelo usuário, após validação)
- [x] Backup local da configuração (com hostname + data/hora no nome)
- [x] Validação da configuração aplicada (VLANs + hostname)
- [x] Rota de auditoria (`/validar`) para checar o switch sem aplicar nada
- [x] Frontend web em Flask

## Tecnologias utilizadas

- **Python 3.12**
- **Flask** — frontend web
- **Netmiko** — automação de rede via SSH
- **Paramiko (<3.0)** — necessário para compatibilidade com algoritmos de
  troca de chave (KEX) mais antigos, usados por imagens Cisco IOS de
  laboratório (EVE-NG)

## Ambiente de testes

O projeto foi desenvolvido e testado em um switch Cisco IOS simulado no
**EVE-NG**, acessível via SSH.

## Estrutura do projeto

```
automacao_sw_cisco_with_front/
├── app.py                  # Aplicação Flask (rotas do frontend)
├── config.py                # Configurações (IP, credenciais, VLANs, hostname alvo)
├── connection.py             # Conexão/desconexão SSH com o switch (Netmiko)
├── vlan_config.py            # Criação das VLANs no switch
├── hostname_config.py        # Alteração do hostname do switch
├── save_config.py            # Salva a configuração na NVRAM (write memory)
├── backup.py                 # Backup local da configuração (com timestamp)
├── validation.py             # Validação da configuração aplicada vs esperada
├── templates/
│   ├── base.html              # Layout base (herdado pelas outras páginas)
│   ├── index.html             # Formulário principal (VLANs + hostname)
│   ├── result.html            # Resultado da aplicação/validação
│   └── salvo.html             # Confirmação de salvamento na NVRAM
├── static/
│   └── style.css              # Estilo visual do frontend
├── backups/                  # Arquivos de backup gerados (ignorados pelo Git)
├── evidencias/
│   └── demo_funcionamento.mp4 # Vídeo de demonstração do projeto
├── teste_hostname.py         # Script de teste: configuração de hostname
├── teste_save.py             # Script de teste: salvamento na NVRAM
├── teste_backup.py           # Script de teste: backup de configuração
├── teste_validacao.py        # Script de teste: validação de configuração
├── requirements.txt          # Dependências do projeto
└── .gitignore
```

## Configuração das VLANs

O projeto cria por padrão as seguintes VLANs:

| ID | Nome            |
|----|-----------------|
| 10 | VLAN_DADOS      |
| 20 | VLAN_VOZ        |
| 50 | VLAN_SEGURANCA  |

> **Nota:** o nome da VLAN 50 foi definido sem acentuação (`VLAN_SEGURANCA`
> em vez de `VLAN_SEGURANÇA`) devido a limitações de compatibilidade entre
> o terminal SSH e o IOS do laboratório, que causavam timeout na
> negociação de comandos via Netmiko.

## Hostname aplicado

Por padrão, o hostname alvo é `SWITCH_AUTOMATIZADO_R1` (definido em
`config.py`), mas pode ser alterado diretamente no formulário do frontend
antes de aplicar a configuração.

## Instalação e execução

### 1. Clonar o repositório

```bash
git clone https://github.com/cgmcosmo/automacao_sw_cisco_with_front.git
cd automacao_sw_cisco_with_front
```

### 2. Criar e ativar um ambiente virtual (recomendado)

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar as dependências

```bash
pip install -r requirements.txt
```

### 4. Ajustar as configurações do switch

Edite o arquivo `config.py` com os dados de conexão do seu switch/lab:

```python
SWITCH_IP = "<IP_DO_SEU_SWITCH>"
SWITCH_USERNAME = "<SEU_USUARIO>"
SWITCH_PASSWORD = "<SUA_SENHA>"
SWITCH_SECRET = "<SUA_SENHA_ENABLE>"
```

> **Nota de segurança:** para simplificar o projeto, as credenciais ficam
> fixas em `config.py`. Essa abordagem é aceitável apenas em ambiente de
> laboratório isolado (como o EVE-NG usado neste projeto); em um cenário
> de produção real, o recomendado seria usar variáveis de ambiente ou um
> cofre de segredos (secrets manager), em vez de credenciais hardcoded.

### 5. Rodar o frontend

```bash
python3 app.py
```

Acesse `http://127.0.0.1:5000` no navegador.

## Como usar o frontend

1. **Tela inicial** — exibe um formulário com o hostname e as VLANs
   pré-preenchidos com os valores padrão de `config.py`. Todos os campos
   são editáveis.
2. **Botão "Aplicar Configuração"** — conecta no switch e, em sequência:
   aplica as VLANs, altera o hostname, gera um backup local da
   configuração e executa a validação. A configuração **não** é salva na
   NVRAM automaticamente nessa etapa.
3. **Tela de resultado** — mostra as VLANs e o hostname aplicados, o
   caminho do backup gerado, e o resultado da validação:
   - Se **tudo estiver correto**, aparece uma confirmação e o botão
     **"Salvar na NVRAM"**.
   - Se houver **divergência**, aparece um alerta detalhando o que não
     bateu com o esperado (e o botão de salvar não é exibido).
4. **Botão "Salvar na NVRAM"** — só aparece após uma validação
   bem-sucedida; persiste a configuração atual do switch
   (`write memory`).
5. **Link "Apenas validar configuração atual"** — disponível na tela
   inicial, permite auditar o estado atual do switch (VLANs e hostname)
   **sem aplicar nenhuma alteração**. Útil para verificar se alguém
   mudou a configuração manualmente, fora do fluxo automatizado.

## Scripts de teste individuais

Cada funcionalidade também pode ser testada isoladamente, fora do
frontend:

```bash
python3 teste_hostname.py     # Aplica o hostname configurado
python3 teste_save.py         # Salva a configuração na NVRAM
python3 teste_backup.py       # Gera um backup local da configuração
python3 teste_validacao.py    # Valida VLANs e hostname aplicados
```

## Backup de configuração

Os backups são salvos localmente na pasta `backups/`, com o nome no
formato:

```
backups/<HOSTNAME>_<AAAA-MM-DD>_<HH-MM-SS>.txt
```

Exemplo: `backups/SWITCH_AUTOMATIZADO_R1_2026-08-19_00-11-01.txt`

> Os arquivos de backup não são versionados no Git (contêm dados de
> configuração do dispositivo), apenas a pasta é mantida via `.gitkeep`.

## Validação de configuração

O módulo `validation.py` compara o estado **atual** do switch (lido
diretamente via SSH: hostname pelo prompt da CLI, VLANs pelo comando
`show vlan brief`) com a configuração **desejada** (definida em
`config.py` ou enviada pelo formulário), verificando:

- Se o hostname atual corresponde ao esperado.
- Se cada VLAN esperada existe no switch, com o nome correto.

Caso haja qualquer divergência, o script reporta exatamente o que não
bateu. Essa validação foi testada em dois cenários:

1. **Logo após aplicar a configuração** (rota `/aplicar`), confirmando
   que o que foi enviado pelo frontend foi realmente aplicado.
2. **De forma independente** (rota `/validar`), simulando uma alteração
   manual no switch (fora do frontend) e confirmando que o script
   detecta corretamente a divergência — essa evidência está registrada
   no vídeo de demonstração.

Exemplo de saída bem-sucedida:
```
Configuração validada com sucesso! Tudo conforme esperado.
```

Exemplo de saída com divergência (VLAN 20 alterada manualmente no switch):
```
Divergências encontradas:
- VLAN 20: nome esperado 'VLAN_VOZ', mas não encontrado na linha: '20 VLAN_TELEFONIA active'
```

## Limitações conhecidas

- A validação verifica apenas VLANs e hostname (conforme escopo do
  projeto), não cobrindo outras configurações do switch (portas,
  trunks, ACLs, etc.).
- As credenciais do switch ficam fixas em `config.py`, o que é aceitável
  apenas em ambiente de laboratório isolado.

## Autor

Desenvolvido por [cgmcosmo](https://github.com/cgmcosmo) como parte de um
desafio técnico de automação de redes.
