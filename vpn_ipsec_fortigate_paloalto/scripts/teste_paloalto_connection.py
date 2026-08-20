from paloalto_connection import conectar_paloalto, testar_conexao

firewall = conectar_paloalto()
info = testar_conexao(firewall)

print("Conectado com sucesso ao Palo Alto!")
print(f"Plataforma: {info.platform}")
print(f"Versão PAN-OS: {info.version}")
print(f"Serial: {info.serial}")