from fortigate_connection import conectar_fortigate, testar_conexao

conexao = conectar_fortigate()
resultado = testar_conexao(conexao)

print("Conectado com sucesso ao FortiGate!")
print(f"Versão FortiOS: {resultado['version']}")
print(f"Build: {resultado['build']}")
print(f"Serial: {resultado['serial']}")