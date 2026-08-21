# Plano de Automação — VPN IPSec entre FortiGate e Palo Alto

## Visão Geral

Este documento descreve o planejamento para automatizar, via scripts Python,
a configuração de uma VPN IPSec site-to-site (route-based) entre um firewall
FortiGate e um firewall Palo Alto, incluindo os parâmetros técnicos, as
ferramentas/APIs envolvidas, os passos lógicos de automação, os desafios de
interoperabilidade entre fabricantes, e a estratégia de validação e alertas.

O ambiente de referência foi montado em laboratório utilizando o EVE-NG, com
a topologia descrita a seguir.

## Topologia de Referência

```
VPC4 (LAN Fortinet) -- R2 (switch L2) -- port1 [FortiGate]
                                                    |
                                        port2 [FortiGate] <--- WAN ---> [Palo Alto] ethernet1/2
                                                                              |
                                                            ethernet1/1 [Palo Alto] -- R3 (switch L2) -- VPC5 (LAN Palo Alto)
```

- R2 e R3 atuam apenas como switches L2, sem participação na automação.
- Toda a lógica de roteamento, políticas e VPN está concentrada nos dois
  firewalls.

## 1. Definição de Parâmetros

### 1.1 Identificação dos peers (WAN)

| Parâmetro | FortiGate | Palo Alto |
|---|---|---|
| Interface WAN | port2 | ethernet1/2 |
| IP WAN (peer local) | 203.0.113.1/30 | 203.0.113.2/30 |
| IP do peer remoto (usado na config do outro lado) | 203.0.113.2 | 203.0.113.1 |

> Endereços na faixa `203.0.113.0/24` (TEST-NET-3, RFC 5737), reservada para
> documentação/exemplos — simula IPs públicos sem conflitar com redes reais.

### 1.2 Redes locais protegidas (Phase 2 / proxy-ids)

| Site | Rede local | Interface | Host de teste |
|---|---|---|---|
| FortiGate | 10.10.10.0/24 | port1 | VPC4 |
| Palo Alto | 10.20.20.0/24 | ethernet1/1 | VPC5 |

### 1.3 Rede de túnel (interface roteada)

| Parâmetro | Valor |
|---|---|
| Rede de túnel | 169.255.1.0/30 |
| IP túnel FortiGate | 169.255.1.1 |
| IP túnel Palo Alto | 169.255.1.2 |

> Optou-se por VPN **route-based** (baseada em interface de túnel numerada)
> em vez de policy-based, por ser o modelo suportado nativamente e de forma
> equivalente em ambos os fabricantes, o que simplifica a automação (rotas
> estáticas/dinâmicas apontando para uma interface, em vez de seletores de
> tráfego amarrados à política de VPN).

### 1.4 Proposta de Phase 1 (IKE)

| Parâmetro | Valor proposto |
|---|---|
| Versão IKE | IKEv2 |
| Método de autenticação | Pre-Shared Key (PSK) |
| Chave pré-compartilhada | Definida em tempo de execução (não versionada no repositório) |
| Algoritmo de criptografia | AES-256 |
| Algoritmo de hash/integridade | SHA-256 |
| Grupo Diffie-Hellman | Group 14 (2048-bit) |
| Tempo de vida da SA (Phase 1) | 28800 segundos (8h) |
| Modo de negociação | IKEv2 (equivalente nos dois fabricantes) |

### 1.5 Proposta de Phase 2 (IPSec)

| Parâmetro | Valor proposto |
|---|---|
| Protocolo | ESP |
| Algoritmo de criptografia | AES-256 |
| Algoritmo de autenticação | SHA-256 |
| PFS (Perfect Forward Secrecy) | Habilitado — Group 14 |
| Tempo de vida da SA (Phase 2) | 3600 segundos (1h) |
| Seletores de tráfego (proxy-ids) | Rede de túnel completa (0.0.0.0/0 quando route-based) ou, alternativamente, rede local × rede remota, conforme necessidade de compatibilidade |

> **Observação importante:** em VPNs route-based, tanto FortiGate quanto
> Palo Alto tipicamente utilizam seletores "any/any" (0.0.0.0/0 ↔ 0.0.0.0/0)
> na Phase 2, deixando o controle de qual tráfego passa pelo túnel a cargo
> das rotas estáticas e das políticas de firewall — não dos proxy-ids. Isso
> reduz um dos principais pontos de incompatibilidade entre fabricantes
> (detalhado na seção 4).

## 2. Identificação de Ferramentas/APIs

### 2.1 FortiGate

- **API REST nativa** (`/api/v2/cmdb/...` e `/api/v2/monitor/...`) — escolha
  principal para este plano. É orientada a objetos JSON, bem documentada, e
  permite tanto configurar (`cmdb`) quanto consultar estado operacional
  (`monitor`), o que cobre tanto a aplicação quanto a validação.
- **Autenticação**: via API Token (gerado a partir de um "API Admin"
  dedicado), enviado no header `Authorization: Bearer <token>`, evitando uso
  de usuário/senha administrativo direto nos scripts.
- **Bibliotecas Python**: `requests` (chamadas diretas à API REST) ou
  `fortiosapi` (wrapper Python que abstrai autenticação e payloads).
- **Alternativa**: SSH com Netmiko (como usado na Parte 1), mas envolve
  parsing de CLI, mais frágil a mudanças de versão — API REST é preferível
  para este caso.

### 2.2 Palo Alto

- **API XML nativa (PAN-OS API)** — baseada em requisições HTTP com
  parâmetros XPath e payloads XML, autenticada via API Key.
- **SDK Python oficial `pan-os-python`** (sucessor do `pandevice`) —
  escolha principal para este plano. Abstrai a complexidade do XML/XPath,
  oferecendo objetos Python para interfaces, zonas, políticas, túneis
  IPSec, etc.
- **Autenticação**: API Key gerada a partir de usuário/senha administrativo
  (uma única vez), reutilizada nas chamadas seguintes via parâmetro
  `key=<api_key>` ou header dedicado.
- **Particularidade**: todas as alterações via API ficam em
  **candidate configuration** até um `commit` explícito — o script precisa
  emitir esse commit como etapa final, e tratar possíveis falhas de commit
  separadamente das falhas de configuração.

### 2.3 Ferramentas de orquestração (alternativas de mais alto nível)

- **Ansible** — módulos prontos para FortiOS (`fortinet.fortios`) e para
  PAN-OS (`paloaltonetworks.panos`), úteis se o objetivo for integrar a
  automação a um pipeline maior (ex: CI/CD de rede).
- **Terraform** — providers específicos para os dois fabricantes,
  interessante para um modelo declarativo/IaC, mas menos flexível para
  lógica condicional de validação do que um script Python dedicado.

Para este plano, a escolha é **Python puro**, mantendo consistência com a
Parte 1 do desafio e permitindo controle fino sobre a lógica de validação e
tratamento de erros entre os dois fabricantes.

## 3. Passos de Automação

Os passos abaixo seguem uma ordem lógica comum aos dois fabricantes, mesmo
que a implementação técnica (chamadas de API) difira entre eles.

1. **Autenticação** — obter token/API key de cada firewall e validar que a
   sessão está ativa antes de prosseguir.
2. **Criação de objetos de endereço** — objetos representando a rede local
   e a rede remota (usados depois em rotas e políticas).
3. **Configuração da interface de túnel** — criação da interface de túnel
   IPSec (route-based), atribuindo o IP correspondente da rede
   `169.255.1.0/30` em cada lado.
4. **Configuração da Phase 1 (IKE Gateway)** — definição do peer remoto
   (IP WAN do outro firewall), método de autenticação (PSK), e proposta de
   criptografia/hash/DH group.
5. **Configuração da Phase 2 (IPSec Tunnel/Crypto Profile)** — associação
   à interface de túnel criada no passo 3, definição da proposta de
   criptografia/autenticação, PFS, e proxy-ids (conforme item 1.5).
6. **Criação de rotas estáticas** — rota para a rede remota apontando para
   a interface de túnel (em ambos os firewalls), permitindo que o tráfego
   destinado à LAN remota seja roteado através do túnel.
7. **Criação de políticas de segurança/firewall** — regras permitindo
   tráfego entre a zona local e a zona do túnel (bidirecional), respeitando
   o modelo de zonas do Palo Alto e o modelo de interface do FortiGate.
8. **Aplicação/commit da configuração** — no FortiGate, a configuração via
   API `cmdb` é aplicada de forma imediata; no Palo Alto, é necessário um
   `commit` explícito ao final de todas as alterações, com tratamento de
   erro caso o commit falhe (nesse caso, a configuração fica pendente em
   candidate config até correção manual ou nova tentativa).
9. **Validação pós-aplicação** — checagem do estado operacional do túnel
   (detalhado na seção 5), não apenas da configuração estática.

## 4. Considerações Específicas

Automatizar a mesma funcionalidade (VPN IPSec) entre dois fabricantes
diferentes exige atenção a diversas diferenças de modelo e comportamento:

- **Diferença de terminologia**: o FortiGate usa "Phase 1 / Phase 2"; o
  Palo Alto usa "IKE Gateway / IPSec Tunnel (Crypto Profile)". A automação
  precisa mapear esses conceitos para uma estrutura de parâmetros comum
  (como a definida na seção 1), traduzindo para o payload específico de
  cada API.
- **Modelo de zonas de segurança**: o Palo Alto exige que toda interface
  pertença a uma zona de segurança, e que políticas sejam definidas entre
  zonas (não apenas entre interfaces). O FortiGate é mais flexível,
  permitindo políticas diretamente entre interfaces. A automação do lado
  Palo Alto precisa necessariamente criar/associar zonas antes de criar
  políticas.
- **Processo de commit em duas etapas (Palo Alto)**: mudanças ficam em
  candidate config até um commit explícito, com possibilidade de validação
  prévia (`validate` via API) antes do commit real. Isso permite um padrão
  de "dry-run" que o FortiGate não oferece da mesma forma — a automação
  pode aproveitar esse recurso para validar a configuração antes de
  efetivamente aplicá-la no Palo Alto.
- **Seletores de tráfego (proxy-ids)**: um dos pontos de maior risco de
  incompatibilidade. Se os seletores não forem simétricos entre os dois
  lados (mesma rede/máscara declarada nos dois firewalls), a Phase 2 não
  estabelece. Adotar VPN route-based com seletores "any/any" (conforme
  seção 1.5) reduz esse risco, delegando o controle de tráfego às rotas e
  políticas, não à Phase 2 em si.
- **Idempotência**: o comportamento ao tentar criar um objeto já existente
  difere entre os fabricantes (um pode retornar erro, outro pode
  sobrescrever silenciosamente). O script de automação precisa verificar a
  existência de cada objeto antes de criar (ou usar operações
  "create-or-update" quando a API suportar), para permitir reexecução
  segura do script sem duplicar ou corromper configuração existente.
- **Gestão de credenciais**: API Token (FortiGate) e API Key (Palo Alto)
  não devem ser hardcoded nos scripts nem versionados no repositório;
  o plano prevê o uso de variáveis de ambiente ou um arquivo de
  configuração local, ignorado pelo Git (seguindo o mesmo cuidado já
  aplicado na Parte 1 deste desafio).
- **Tempo de convergência assimétrico**: a negociação IKE pode ser
  iniciada por qualquer um dos lados; em ambientes de automação, é comum
  configurar ambos os firewalls e depois "provocar" a negociação (ex: gerar
  tráfego de teste) em vez de assumir que o túnel sobe automaticamente
  apenas com a configuração aplicada.

## 5. Validação de Configuração e Alertas

A estratégia de validação é dividida em duas camadas, refletindo a
diferença entre "a configuração está correta" e "o túnel está realmente
funcionando":

### 5.1 Validação de configuração aplicada

Consulta, via API, aos objetos configurados em cada firewall, comparando
com os parâmetros desejados (mesmo princípio usado na Parte 1 deste
desafio, com VLANs e hostname):

- **FortiGate**: `GET /api/v2/cmdb/vpn.ipsec/phase1-interface` e
  `GET /api/v2/cmdb/vpn.ipsec/phase2-interface`, comparando peer IP,
  proposta de criptografia e interface de túnel com o esperado.
- **Palo Alto**: consulta via `pan-os-python` aos objetos `IkeGateway` e
  `IpsecTunnel` (ou requisição XML/XPath equivalente), comparando os
  mesmos parâmetros.

### 5.2 Validação de estado operacional (o túnel subiu de verdade?)

Checagem do status real da SA (Security Association) em cada firewall:

- **FortiGate**: `GET /api/v2/monitor/vpn/ipsec` — retorna o status atual
  das SAs de Phase 1 e Phase 2 (up/down, tempo de vida restante, bytes
  trafegados).
- **Palo Alto**: comando `show vpn ike-sa` e `show vpn ipsec-sa` (via API
  de tipo `op`, comando operacional), retornando o estado da negociação
  IKE e das SAs IPSec.

### 5.3 Teste de conectividade fim a fim (opcional)

Um script de teste dispararia pings (ou outra checagem, como TCP connect)
de um host atrás de um firewall para um host atrás do outro (ex: VPC4 →
VPC5), confirmando que o tráfego realmente atravessa o túnel — essa é a
validação mais próxima do "usuário final", complementando as duas
anteriores.

### 5.4 Estratégia de alertas

Os alertas seriam categorizados por severidade, similar à abordagem já
usada no frontend da Parte 1:

- **Aviso (divergência de configuração)**: algum parâmetro configurado
  (proposta de criptografia, IP de peer, rede protegida) não corresponde
  ao valor desejado, mas o túnel pode ainda estar operacional. Reportado
  como alerta informativo, sem indicar necessariamente indisponibilidade.
- **Crítico (túnel down)**: a Phase 1 ou Phase 2 não está estabelecida
  (SA ausente ou expirada) — indica problema operacional real, exigindo
  ação imediata. Esse alerta seria priorizado sobre divergências de
  configuração, já que impacta diretamente a disponibilidade do serviço.
- **Crítico (falha de commit/aplicação)**: no Palo Alto, se o commit
  falhar, a configuração pretendida nunca chega a ser aplicada — esse
  cenário precisa de alerta imediato, distinto de uma divergência
  encontrada após a aplicação.

Em uma implementação completa, esses alertas poderiam ser exibidos em um
frontend (seguindo o mesmo padrão da Parte 1, com rota de validação
independente da aplicação), enviados por e-mail/webhook, ou integrados a
uma ferramenta de monitoramento externa.

## 6. Escopo dos Scripts de Exemplo (Opcional)

Conforme o caráter opcional desta entrega, a pasta `scripts/` deste
diretório contém exemplos conceituais/parciais da estrutura Python
proposta, organizados por responsabilidade (seguindo o mesmo padrão
modular adotado na Parte 1):

```
scripts/
├── config_vpn.py           # Parâmetros centralizados (IPs, redes, propostas)
├── fortigate_connection.py # Autenticação e sessão com a API REST do FortiGate
├── fortigate_vpn.py        # Criação de Phase1/Phase2/interface de túnel (FortiGate)
├── paloalto_connection.py  # Autenticação e sessão via pan-os-python
├── paloalto_vpn.py         # Criação de IKE Gateway/IPSec Tunnel (Palo Alto)
├── validation.py           # Validação de configuração e estado operacional
└── test_connectivity.py    # Teste de conectividade fim a fim através do túnel
```

Esses scripts representam a implementação prática do plano descrito acima,
e podem ser testados contra o ambiente de laboratório (FortiGate e Palo
Alto no EVE-NG) descrito na seção "Topologia de Referência".

## 7. Notas de Implementação no Ambiente de Laboratório

Durante a implementação dos scripts de conexão contra o ambiente EVE-NG,
foi identificada uma limitação específica da imagem utilizada:

- **FortiGate (VM64-KVM, versão de avaliação/sem licença)**: o serviço
  administrativo HTTPS (porta 443) não respondia corretamente às
  requisições da API REST, mesmo com `allowaccess https` habilitado na
  interface e Trusted Hosts configurado — a conexão era encerrada durante
  o handshake TLS (`Connection reset by peer`), enquanto o acesso via
  HTTP (porta 80) funcionava normalmente. Diagnóstico via CLI
  (`diagnose sys tcpsock`) confirmou que nenhum processo estava
  efetivamente escutando na porta 443, um comportamento conhecido em
  algumas imagens de avaliação/não licenciadas do FortiGate.
- Como solução para viabilizar o desenvolvimento e teste no ambiente de
  laboratório, o script `fortigate_connection.py` foi ajustado para
  utilizar **HTTP** em vez de HTTPS na comunicação com a API REST.
- **Esta decisão é válida exclusivamente para o ambiente de laboratório
  isolado.** Em um ambiente de produção real, a comunicação com a API do
  FortiGate deve **sempre** utilizar HTTPS, com verificação de
  certificado habilitada (idealmente com certificado assinado por uma CA
  confiável, não autoassinado), para garantir a confidencialidade do
  token de autenticação em trânsito.
  
## Autor

Desenvolvido por [cgmcosmo](https://github.com/cgmcosmo) como parte de um
desafio técnico de automação de redes — Parte 2 (Planejamento de VPN
IPSec entre FortiGate e Palo Alto).
