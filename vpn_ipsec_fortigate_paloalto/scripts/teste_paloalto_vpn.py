from paloalto_connection import conectar_paloalto
from paloalto_vpn import configurar_vpn_completa

firewall = conectar_paloalto()
resultados = configurar_vpn_completa(firewall)

print("Resultado da configuração da VPN no Palo Alto:")
for etapa, status in resultados.items():
    print(f"  [{status.split(':')[0]}] {etapa}: {status}")