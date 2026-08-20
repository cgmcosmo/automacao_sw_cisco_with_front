from flask import Flask, render_template, request
import config
from connection import conectar_switch, desconectar_switch
from vlan_config import configurar_vlans
from hostname_config import configurar_hostname
from backup import fazer_backup
from validation import validar_configuracao
from save_config import salvar_configuracao

app = Flask(__name__)


@app.route("/")
def index():
    """
    Exibe o formulário principal com as VLANs e o hostname pré-preenchidos
    com os valores padrão definidos em config.py, mas editáveis pelo usuário.
    """
    return render_template("index.html", vlans=config.VLANS, hostname=config.HOSTNAME_TARGET)


@app.route("/aplicar", methods=["POST"])
def aplicar():
    """
    Recebe os dados do formulário, conecta no switch e aplica:
    VLANs -> hostname -> backup -> validação.
    Não salva na NVRAM ainda (isso é feito em uma etapa separada).
    """
    hostname = request.form.get("hostname")

    total_vlans = int(request.form.get("total_vlans", 0))
    vlans = []
    for i in range(total_vlans):
        vlan_id = request.form.get(f"vlan_id_{i}")
        vlan_name = request.form.get(f"vlan_name_{i}")
        vlans.append({"id": int(vlan_id), "name": vlan_name})

    conexao = conectar_switch()

    configurar_vlans(conexao, vlans)
    configurar_hostname(conexao, hostname)

    caminho_backup = fazer_backup(conexao, hostname)
    resultado_validacao = validar_configuracao(conexao, vlans, hostname)

    desconectar_switch(conexao)

    return render_template(
        "result.html",
        hostname=hostname,
        vlans=vlans,
        backup=caminho_backup,
        validacao=resultado_validacao,
        somente_validacao=False,
    )


@app.route("/salvar", methods=["POST"])
def salvar():
    """
    Conecta no switch e salva a configuração atual na NVRAM (write memory).
    Chamado somente após o usuário confirmar que a validação foi bem-sucedida.
    """
    conexao = conectar_switch()
    resultado = salvar_configuracao(conexao)
    desconectar_switch(conexao)

    return render_template("salvo.html", resultado=resultado)


@app.route("/validar")
def validar():
    """
    Conecta no switch e valida a configuração ATUAL (sem aplicar nada),
    comparando com os valores padrão definidos em config.py.
    Útil para auditar o switch sem alterar nenhuma configuração.
    """
    conexao = conectar_switch()
    resultado_validacao = validar_configuracao(conexao, config.VLANS, config.HOSTNAME_TARGET)
    desconectar_switch(conexao)

    return render_template(
        "result.html",
        hostname=config.HOSTNAME_TARGET,
        vlans=config.VLANS,
        backup=None,
        validacao=resultado_validacao,
        somente_validacao=True,
    )


if __name__ == "__main__":
    app.run(debug=True)