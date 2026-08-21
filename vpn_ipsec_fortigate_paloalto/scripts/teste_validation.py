from fortigate_connection import conectar_fortigate
from paloalto_connection import conectar_paloalto
from validation import validar_vpn_completa

conexao_forti = conectar_fortigate()
firewall_pa = conectar_paloalto()

resultado = validar_vpn_completa(conexao_forti, firewall_pa)

print("=== Validação da VPN IPSec ===\n")

print(f"FortiGate - IKE up: {resultado['fortigate']['ike_up']} | IPSec up: {resultado['fortigate']['ipsec_up']}")
print(f"Palo Alto - IKE up: {resultado['paloalto']['ike_up']} | IPSec up: {resultado['paloalto']['ipsec_up']}")

print("\nAlertas:")
for alerta in resultado["alertas"]:
    simbolo = "🔴" if alerta["severidade"] == "critico" else "🟢"
    print(f"  {simbolo} [{alerta['severidade'].upper()}] {alerta['mensagem']}")

print(f"\nStatus geral: {'VÁLIDO' if resultado['valido'] else 'FALHA DETECTADA'}")