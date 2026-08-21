from fortigate_connection import conectar_fortigate
from fortigate_vpn import configurar_vpn_completa

conexao = conectar_fortigate()
resultados = configurar_vpn_completa(conexao)

print("Resultado da configuração da VPN no FortiGate:")
for etapa, status in resultados.items():
    simbolo = "OK" if status in (200, 201) else "ERRO"
    print(f"  [{simbolo}] {etapa}: HTTP {status}")