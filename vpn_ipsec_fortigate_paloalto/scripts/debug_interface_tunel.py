from fortigate_connection import conectar_fortigate
from fortigate_vpn import criar_interface_tunel

conexao = conectar_fortigate()
resposta = criar_interface_tunel(conexao)

print(f"Status: {resposta.status_code}")
print(f"Corpo da resposta: {resposta.text}")