import requests
from fortigate_connection import conectar_fortigate

conexao = conectar_fortigate()

print("=== Phase 1 configuradas ===")
resp = requests.get(f"{conexao['base_url']}/cmdb/vpn.ipsec/phase1-interface", headers=conexao["headers"])
for item in resp.json().get("results", []):
    print(f"  - {item['name']} (peer: {item.get('remote-gw')})")

print("\n=== Phase 2 configuradas ===")
resp = requests.get(f"{conexao['base_url']}/cmdb/vpn.ipsec/phase2-interface", headers=conexao["headers"])
for item in resp.json().get("results", []):
    print(f"  - {item['name']} (phase1: {item.get('phase1name')})")

print("\n=== Interfaces de túnel ===")
resp = requests.get(f"{conexao['base_url']}/cmdb/system/interface", headers=conexao["headers"])
for item in resp.json().get("results", []):
    if item.get("type") == "tunnel":
        print(f"  - {item['name']} (ip: {item.get('ip')})")