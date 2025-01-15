from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# Configuração do Banco de Dados PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost/gestao_estoque'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'sua_secret_key_aqui'

db = SQLAlchemy(app)

# Modelo do Banco de Dados
class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    protocolo = db.Column(db.String(20), nullable=False)
    atendente = db.Column(db.String(50), nullable=False)
    rating_atendente = db.Column(db.Integer, nullable=False)
    rating_recomendacao = db.Column(db.Integer, nullable=False)
    comentario = db.Column(db.Text)
    data = db.Column(db.DateTime, default=datetime.utcnow)

# Página Principal
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

# Receber Feedback
@app.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    data = request.json
    protocolo = data.get('protocolo')
    atendente = data.get('atendente')
    rating_atendente = data.get('rating_atendente')
    rating_recomendacao = data.get('rating_recomendacao')
    comentario = data.get('comentario')

    # Verifica campos obrigatórios
    if not protocolo or not atendente or not rating_atendente or not rating_recomendacao:
        return jsonify({"error": "Campos obrigatórios ausentes"}), 400

    # Salvar Feedback no Banco de Dados
    new_feedback = Feedback(
        protocolo=protocolo,
        atendente=atendente,
        rating_atendente=rating_atendente,
        rating_recomendacao=rating_recomendacao,
        comentario=comentario
    )
    db.session.add(new_feedback)
    db.session.commit()

    return jsonify({"redirect": url_for('obrigado')}), 200

# Página de Agradecimento
@app.route('/obrigado', methods=['GET'])
def obrigado():
    return render_template('obrigado.html')

# Filtro de atendente
@app.route('/get_filtered_feedback', methods=['GET'])
def get_filtered_feedback():
    atendente = request.args.get('atendente')  # Obtém o atendente da requisição
    if not atendente:
        return jsonify({"error": "Atendente não informado"}), 400

    # Filtra os feedbacks pelo atendente
    feedbacks = Feedback.query.filter_by(atendente=atendente).all()

    if not feedbacks:
        return jsonify({
            "grafico": [0, 0, 0, 0, 0],
            "feedbacks": []
        })

    # Calcula a distribuição de notas
    grafico_notas = [0, 0, 0, 0, 0]
    for feedback in feedbacks:
        if 1 <= feedback.rating_atendente <= 5:
            grafico_notas[feedback.rating_atendente - 1] += 1

    return jsonify({
        "grafico": grafico_notas,
        "feedbacks": [
            {
                "protocolo": fb.protocolo,
                "atendente": fb.atendente,
                "rating": fb.rating_atendente,
                "comentario": fb.comentario,
                "data": fb.data.strftime('%d/%m/%Y %H:%M'),
            } for fb in feedbacks
        ]
    })


#Grafico media geral
@app.route('/get_general_feedback', methods=['GET'])
def get_general_feedback():
    feedbacks = Feedback.query.all()

    # Calcula a distribuição geral de notas
    grafico_notas = [0, 0, 0, 0, 0]
    for feedback in feedbacks:
        if 1 <= feedback.rating_atendente <= 5:
            grafico_notas[feedback.rating_atendente - 1] += 1

    return jsonify({
        "grafico": grafico_notas
    })



# Dashboard para visualização
@app.route('/dashboard', methods=['GET'])
def dashboard():
    feedbacks = Feedback.query.all()
    avg_rating_atendente = db.session.query(db.func.avg(Feedback.rating_atendente)).scalar() or 0
    avg_rating_recomendacao = db.session.query(db.func.avg(Feedback.rating_recomendacao)).scalar() or 0

    avg_rating_atendente = round(avg_rating_atendente, 2)
    avg_rating_recomendacao = round(avg_rating_recomendacao, 2)

    grafico_notas_atendente = [0, 0, 0, 0, 0]
    grafico_notas_recomendacao = [0, 0, 0, 0, 0]

    for feedback in feedbacks:
        if 1 <= feedback.rating_atendente <= 5:
            grafico_notas_atendente[feedback.rating_atendente - 1] += 1
        if 1 <= feedback.rating_recomendacao <= 5:
            grafico_notas_recomendacao[feedback.rating_recomendacao - 1] += 1

    # Lista de atendentes únicos
    atendentes = db.session.query(Feedback.atendente).distinct().all()
    atendentes = [at[0] for at in atendentes]  # Formata a lista para um array simples

    return render_template(
        'dashboard.html',
        feedbacks=feedbacks,
        media_atendente=avg_rating_atendente,
        media_recomendacao=avg_rating_recomendacao,
        grafico_notas_atendente=grafico_notas_atendente,
        grafico_notas_recomendacao=grafico_notas_recomendacao,
        atendentes=atendentes  # Envia a lista de atendentes
    )


if __name__ == '__main__':
    app.run(debug=True)
