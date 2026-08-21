from connectivity import testar_conectividade_completa

resultado = testar_conectividade_completa()

simbolo = "✅" if resultado["severidade"] == "info" else "🔴"
print(f"{simbolo} {resultado['mensagem']}")
print(f"\nSaída bruta do ping:\n{resultado['resultado']['saida_bruta']}")