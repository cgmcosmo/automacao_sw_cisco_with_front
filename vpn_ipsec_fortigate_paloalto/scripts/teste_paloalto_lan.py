from paloalto_connection import conectar_paloalto
from paloalto_lan import configurar_lan

firewall = conectar_paloalto()
resultados = configurar_lan(firewall)

print("Resultado da configuração da LAN no Palo Alto:")
for etapa, status in resultados.items():
    print(f"  [{status.split(':')[0]}] {etapa}: {status}")

# Commit final
try:
    firewall.commit(sync=True)
    print("\nCommit realizado com sucesso!")
except Exception as erro:
    print(f"\nErro no commit: {erro}")