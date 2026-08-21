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
IPSEC_PSK = "<DEFINA_UMA_CHAVE_FORTE_AQUI>"

# Proposta de Phase 1 (IKE)
PHASE1_PROPOSAL = {
    "ike_version": "2",
    "encryption": "aes256",
    "hash": "sha256",
    "dh_group": "14",
    "lifetime_seconds": 28800,
}

# Proposta de Phase 2 (IPSec)
PHASE2_PROPOSAL = {
    "protocol": "esp",
    "encryption": "aes256",
    "authentication": "sha256",
    "pfs_group": "14",
    "lifetime_seconds": 3600,
}

# Nomes lógicos usados na configuração (túnel, interface, política)
TUNNEL_NAME = "VPN_FORTI_PALOALTO"