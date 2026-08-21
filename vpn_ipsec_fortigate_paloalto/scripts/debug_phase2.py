from fortigate_connection import conectar_fortigate
from fortigate_vpn import criar_phase2

conexao = conectar_fortigate()
resposta = criar_phase2(conexao)

print(f"Status: {resposta.status_code}")
print(f"Corpo da resposta: {resposta.text}")