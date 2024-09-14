from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)

# Configurando o caminho do banco de dados SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///jogadores.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializando o banco de dados
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Definindo o modelo para a tabela de jogadores
class Jogador(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    presente = db.Column(db.Boolean, default=False)

# Cria o banco de dados
with app.app_context():
    db.create_all()

def ler_jogadores_arquivo():
    try:
        with open('jogadores.txt', 'r') as file:
            return [linha.strip() for linha in file.readlines()]
    except FileNotFoundError:
        return []

def salvar_jogadores_arquivo(jogadores):
    with open('jogadores.txt', 'w') as file:
        for jogador in jogadores:
            file.write(f"{jogador}\n")

@app.route('/')
def index():
    jogadores = Jogador.query.all()  # Carrega todos os jogadores do banco de dados
    total_jogadores = len(jogadores)  # Conta o número total de jogadores
    jogadores_faltando = 15 - total_jogadores  # Calcula quantos jogadores faltam para completar 15
    jogadores_com_numero = [(i + 1, jogador) for i, jogador in enumerate(jogadores)]  # Adiciona numeração
    return render_template('index.html', jogadores=jogadores_com_numero, jogadores_faltando=jogadores_faltando)

@app.route('/adicionar', methods=['POST'])
def adicionar_jogador():
    nome = request.form['nome']
    if nome:  # Verifica se o nome não está vazio
        novo_jogador = Jogador(nome=nome)
        db.session.add(novo_jogador)  # Adiciona o jogador ao banco
        db.session.commit()  # Confirma a inserção

        # Atualiza o arquivo
        jogadores = ler_jogadores_arquivo()
        jogadores.append(nome)
        salvar_jogadores_arquivo(jogadores)

    return redirect(url_for('index'))

@app.route('/marcar_presenca/<int:id>')
def marcar_presenca(id):
    jogador = Jogador.query.get(id)  # Busca o jogador pelo ID
    if jogador:  # Verifica se o jogador existe
        jogador.presente = not jogador.presente  # Alterna o status de presença
        db.session.commit()  # Confirma a atualização
    return redirect(url_for('index'))

@app.route('/excluir/<int:id>')
def excluir_jogador(id):
    jogador = Jogador.query.get(id)  # Busca o jogador pelo ID
    if jogador:  # Verifica se o jogador existe
        db.session.delete(jogador)  # Remove o jogador do banco de dados
        db.session.commit()  # Confirma a exclusão

        # Atualiza o arquivo
        jogadores = ler_jogadores_arquivo()
        jogadores = [j for j in jogadores if j != jogador.nome]
        salvar_jogadores_arquivo(jogadores)

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
