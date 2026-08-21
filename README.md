# Automação de Rede: Switch Cisco (Parte 1) e VPN IPSec FortiGate/Palo Alto (Parte 2)

Repositório com dois desafios técnicos de automação de redes: configuração
de switches Cisco via frontend Flask (Parte 1), e planejamento/automação de
uma VPN IPSec entre FortiGate e Palo Alto (Parte 2).

## Parte 1 — Automação de Switch Cisco com Frontend de Configuração

Projeto de automação em Python que se conecta via SSH a um switch Cisco
(testado em laboratório EVE-NG) para configurar VLANs, alterar o hostname,
salvar a configuração na NVRAM, gerar backups locais e validar se a
configuração aplicada corresponde à configuração desejada — tudo através
de um frontend web feito em Flask.

**Status:** completo (backend + frontend + validação + evidências).

**Como executar:** ver instruções detalhadas mais abaixo neste documento,
na seção "Instalação e execução".

### Vídeo de demonstração (Parte 1)

Um vídeo com o funcionamento completo do projeto (formulário, aplicação
da configuração, validação, salvamento na NVRAM e detecção de
divergência) está disponível em [`evidencias/demo_funcionamento.mp4`](evidencias/demo_funcionamento.mp4).

---

## Parte 2 — VPN IPSec entre FortiGate e Palo Alto

Planejamento e automação (em Python) da configuração de uma VPN IPSec
site-to-site entre um firewall FortiGate e um firewall Palo Alto,
incluindo definição de parâmetros, ferramentas/APIs utilizadas, scripts
de configuração para ambos os fabricantes, validação de estado
operacional e teste de conectividade fim a fim.

**Status:** completo — não apenas planejado, mas implementado e testado
contra um ambiente real (EVE-NG), com a VPN estabelecida com sucesso e
tráfego real confirmado entre as redes locais dos dois firewalls.

📄 **Documento principal:** [`vpn_ipsec_fortigate_paloalto/vpn_ipsec_plan.md`](vpn_ipsec_fortigate_paloalto/vpn_ipsec_plan.md)
— contém parâmetros da VPN, ferramentas/APIs, passos de automação,
considerações específicas entre fabricantes, estratégia de validação e
alertas, e um relato detalhado das descobertas práticas obtidas durante
a implementação real.

📁 **Scripts de automação:** [`vpn_ipsec_fortigate_paloalto/scripts/`](vpn_ipsec_fortigate_paloalto/scripts/)

```
vpn_ipsec_fortigate_paloalto/
├── vpn_ipsec_plan.md            # Documento de planejamento completo
└── scripts/
    ├── config_vpn.py              # Parâmetros centralizados (IPs, redes, propostas)
    ├── fortigate_connection.py    # Conexão com a API REST do FortiGate
    ├── fortigate_vpn.py           # Configuração da VPN no FortiGate (Phase 1/2, rota, políticas)
    ├── fortigate_lan.py           # Configuração da LAN local do FortiGate
    ├── paloalto_connection.py     # Conexão com o Palo Alto via pan-os-python
    ├── paloalto_vpn.py            # Configuração da VPN no Palo Alto (IKE Gateway, IPSec Tunnel, zonas, rota)
    ├── paloalto_lan.py            # Configuração da LAN local do Palo Alto
    ├── validation.py              # Validação do estado operacional da VPN (IKE/IPSec SA) em ambos os firewalls
    ├── connectivity.py            # Teste de conectividade fim a fim através do túnel (ping via SSH)
    └── teste_*.py                 # Scripts de teste individuais para cada módulo acima
```

### Resultados obtidos no laboratório

- ✅ VPN configurada via automação em ambos os fabricantes (FortiGate via
  API REST; Palo Alto via SDK `pan-os-python`)
- ✅ Túnel confirmado como `Established`/`Mature` em ambos os lados
  (`diagnose vpn ike gateway list` no FortiGate; `show vpn ike-sa` no
  Palo Alto)
- ✅ Validação automatizada testada em ciclo completo: sucesso → falha
  simulada (flush manual da SA) → recuperação automática
- ✅ Conectividade real confirmada: ping entre as redes locais dos dois
  firewalls com 0% de perda de pacotes

### Tecnologias utilizadas

- **Python 3.12**
- **Requests** — automação do FortiGate via API REST
- **pan-os-python** — SDK oficial para automação do Palo Alto
- **Netmiko** — teste de conectividade via SSH/CLI

---

## Instalação e execução (Parte 1)

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

## Como usar o frontend (Parte 1)

1. **Tela inicial** — exibe um formulário com o hostname e as VLANs
   pré-preenchidos com os valores padrão de `config.py`. Todos os campos
   são editáveis.
2. **Botão "Aplicar Configuração"** — conecta no switch e, em sequência:
   aplica as VLANs, altera o hostname, gera um backup local da
   configuração e executa a validação.
3. **Tela de resultado** — mostra o resultado da validação; se tudo
   estiver correto, exibe o botão **"Salvar na NVRAM"**; se houver
   divergência, exibe um alerta detalhado.
4. **Link "Apenas validar configuração atual"** — permite auditar o
   estado atual do switch sem aplicar nenhuma alteração.

## Scripts de teste individuais (Parte 1)

```bash
python3 teste_hostname.py     # Aplica o hostname configurado
python3 teste_save.py         # Salva a configuração na NVRAM
python3 teste_backup.py       # Gera um backup local da configuração
python3 teste_validacao.py    # Valida VLANs e hostname aplicados
```

## Backup de configuração (Parte 1)

Os backups são salvos localmente na pasta `backups/`, com o nome no
formato `<HOSTNAME>_<AAAA-MM-DD>_<HH-MM-SS>.txt`. Não são versionados no
Git (contêm dados de configuração do dispositivo).

## Autor

Desenvolvido por [cgmcosmo](https://github.com/cgmcosmo) como parte de um
desafio técnico de automação de redes.
