# Parâmetros de conexão com os firewalls (ajuste com os dados reais do seu lab)

FORTIGATE_HOST = "192.168.19.141"
FORTIGATE_API_TOKEN = "fnG3mNkb0cq6g0gNpzNd7z06yb1ycs"

PALOALTO_HOST = "192.168.19.142"
PALOALTO_USERNAME = "admin"
PALOALTO_PASSWORD = "admin"
PALOALTO_API_KEY = "LUFRPT14MW5xOEo1R09KVlBZNnpnemh0VHRBOWl6TGM9bXcwM3JHUGVhRlNiY0dCR0srNERUQT09"

# Endereços WAN (peers da VPN)
FORTIGATE_WAN_IP = "203.0.113.1"
PALOALTO_WAN_IP = "203.0.113.2"

# Redes locais protegidas (Phase 2 / proxy-ids)
FORTIGATE_LOCAL_NETWORK = "10.10.10.0/24"
PALOALTO_LOCAL_NETWORK = "10.20.20.0/24"

# Rede de túnel (interface roteada)
TUNNEL_NETWORK = "169.255.1.0/30"
FORTIGATE_TUNNEL_IP = "169.255.1.1"
PALOALTO_TUNNEL_IP = "169.255.1.2"

# Pre-shared key (defina localmente, nunca versione a chave real no Git)
IPSEC_PSK = "pskcgmcosmomevarejo"

# Proposta de Phase 1 (IKE)
# NOTA: valores reduzidos para DES devido a restricao de licenca da imagem
# FortiGate VM64-KVM de avaliacao, que nao disponibiliza algoritmos AES
# para VPN IPSec em dispositivos nao registrados (comportamento intencional
# da Fortinet, ligado a controles de exportacao de criptografia). Em
# ambiente de producao licenciado, os valores corretos seriam
# encryption=aes256, hash=sha256, conforme documentado no plano
# (vpn_ipsec_plan.md, secao 1.4).
PHASE1_PROPOSAL = {
    "ike_version": "2",
    "encryption": "des",
    "hash": "sha256",
    "dh_group": "14",
    "lifetime_seconds": 28800,
}

# Proposta de Phase 2 (IPSec)
# NOTA: mesma restricao de licenca aplicada aqui - ver comentario acima.
# Em producao licenciada, o valor correto seria encryption=aes256.
PHASE2_PROPOSAL = {
    "protocol": "esp",
    "encryption": "des",
    "authentication": "sha256",
    "pfs_group": "14",
    "lifetime_seconds": 3600,
}

# Nomes lógicos usados na configuração (túnel, interface, política)
TUNNEL_NAME = "VPN_FTGT_PA"