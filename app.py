from flask import Flask, render_template
import config

app = Flask(__name__)


@app.route("/")
def index():
    """
    Exibe o formulário principal com as VLANs e o hostname pré-preenchidos
    com os valores padrão definidos em config.py, mas editáveis pelo usuário.
    """
    return render_template("index.html", vlans=config.VLANS, hostname=config.HOSTNAME_TARGET)


if __name__ == "__main__":
    app.run(debug=True)