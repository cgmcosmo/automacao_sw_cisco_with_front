import requests
from fortigate_connection import conectar_fortigate
import config_vpn

conexao = conectar_fortigate()

url = f"{conexao['base_url']}/cmdb/vpn.ipsec/phase1-interface/{config_vpn.TUNNEL_NAME}"
payload = {
    "proposal": "aes256-sha256"
}

resposta = requests.put(url, headers=conexao["headers"], json=payload)
print(f"Status: {resposta.status_code}")
print(f"Corpo: {resposta.text}")