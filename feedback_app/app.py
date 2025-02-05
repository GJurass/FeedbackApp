from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
from urllib.parse import quote

app = Flask(__name__)

# Configuração do Banco de Dados MySQL hospedado em Docker
DB_USER = "sammy"
DB_PASSWORD = quote("Startalk@2025")  # Codifica a senha corretamente
DB_HOST = "159.203.163.219"
DB_PORT = "3306"
DB_NAME = "linkfirepesquisa"

app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'sua_secret_key_aqui'

db = SQLAlchemy(app)

# Modelo do Banco de Dados
class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    protocolo = db.Column(db.String(20), nullable=False, default='TESTE123')
    atendente = db.Column(db.String(50), nullable=False, default='ATENDENTE_FIXO')
    rating = db.Column(db.Integer, nullable=False)
    comentario = db.Column(db.Text, nullable=True)
    data = db.Column(db.DateTime, default=datetime.utcnow)

# Página Principal
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

# Receber Feedback
@app.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    try:
        data = request.json
        protocolo = data.get('protocolo', 'TESTE123')
        atendente = data.get('atendente', 'ATENDENTE_FIXO')
        rating = data.get('rating')
        comentario = data.get('comentario')

        if not rating:
            return jsonify({"error": "Campos obrigatórios ausentes"}), 400

        new_feedback = Feedback(
            protocolo=protocolo,
            atendente=atendente,
            rating=rating,
            comentario=comentario
        )
        db.session.add(new_feedback)
        db.session.commit()

        return jsonify({"redirect": "/obrigado"}), 200
    except Exception as e:
        print(f"Erro ao processar feedback: {e}")
        return jsonify({"error": "Erro interno no servidor"}), 500

# Página de Agradecimento
@app.route('/obrigado', methods=['GET'])
def obrigado():
    return render_template('obrigado.html')

# Dashboard para visualização
@app.route('/dashboard', methods=['GET'])
def dashboard():
    try:
        feedbacks = Feedback.query.all()
        avg_rating = db.session.query(db.func.avg(Feedback.rating)).scalar() or 0
        avg_rating = round(avg_rating, 2)

        grafico_notas = [0] * 10
        for feedback in feedbacks:
            if 1 <= feedback.rating <= 10:
                grafico_notas[feedback.rating - 1] += 1

        return render_template(
            'dashboard.html',
            feedbacks=feedbacks,
            media_rating=avg_rating,
            grafico_notas=grafico_notas
        )
    except Exception as e:
        print(f"Erro ao carregar dashboard: {e}")
        return jsonify({"error": "Erro ao carregar dashboard"}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Criar tabelas antes de iniciar o servidor
    app.run(debug=True, host='0.0.0.0', port=5000)
