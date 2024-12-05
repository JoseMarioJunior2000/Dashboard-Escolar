from flask import Blueprint, render_template, request
from services.repository_instances import aspirante_repo

detalhes_blueprinte = Blueprint('detalhes', __name__)

@detalhes_blueprinte.route('/aspirante/detalhes', methods=['GET'])
def detalhes_aspirante():
    aspirante = None
    mensagem = ""
    
    nome = request.args.get('nome', '').strip().upper()
    email = request.args.get('email', '').strip()
    idade = request.args.get('idade', '').strip()

    # Verifica se ao menos um campo foi preenchido
    if nome or email or idade:
        if idade.isdigit():
            idade = int(idade)
        else:
            idade = None  # Caso a idade não seja um número, define como None

        aspirante = aspirante_repo.select(nome=nome or None, email=email or None, idade=idade)

        if not aspirante:
            mensagem = "Nenhum aspirante encontrado com os critérios fornecidos."
    else:
        mensagem = "Por favor, preencha pelo menos um dos campos para buscar um aspirante."

    return render_template('aspirantes_detalhes.html', aspirante=aspirante, mensagem=mensagem)