# Dados de conexão com o switch no EVE-NG
# LAB EVE-NG
SWITCH_IP = "192.168.1.1"
SWITCH_USERNAME = "admin"
SWITCH_PASSWORD = "admin"
SWITCH_SECRET = "admin"  # senha do modo enable, se houver

# Dispositivo
SWITCH_DEVICE_TYPE = "cisco_ios"

# Hostname
HOSTNAME_TARGET = "SWITCH_AUTOMATIZADO"

# VLANs do projeto
VLANS = [
    {"id": 10, "name": "VLAN_DADOS"},
    {"id": 20, "name": "VLAN_VOZ"},
    {"id": 50, "name": "VLAN_SEGURANÇA"},
]

# Pasta onde os backups de configuração serão salvos
BACKUP_DIR = "backups"