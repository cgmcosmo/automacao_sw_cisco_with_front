from flask import Flask, render_template, request
import config
from connection import conectar_switch, desconectar_switch
from vlan_config import configurar_vlans
from hostname_config import configurar_hostname
from backup import fazer_backup
from validation import validar_configuracao

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
    )


if __name__ == "__main__":
    app.run(debug=True)