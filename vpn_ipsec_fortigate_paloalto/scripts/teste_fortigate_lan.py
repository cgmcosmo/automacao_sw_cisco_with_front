from fortigate_connection import conectar_fortigate
from fortigate_lan import configurar_lan

conexao = conectar_fortigate()
resultados = configurar_lan(conexao)

print("Resultado da configuração da LAN no FortiGate:")
for etapa, status in resultados.items():
    print(f"  [{status.split(':')[0]}] {etapa}: {status}")