from flask import Blueprint, render_template, request, current_app
from services.repository_instances import encontro_repo, professor_repo, atividades_repo, aspirante_repo
import pandas as pd
from services.validations import validar_dados_encontro
import os
from werkzeug.utils import secure_filename
import json

trilhas_blueprinte = Blueprint('trilhas', __name__)

@trilhas_blueprinte.route('/encontros', methods=['GET', 'POST'])
def listar_encontros():
    encontros = None
    if request.method == 'POST':
        trilha = request.form.get('trilha')
        data_inicial = request.form.get('data_inicial')
        data_final = request.form.get('data_final')
        hora = request.form.get('hora')
        modulo = request.form.get('modulo')
        assunto = request.form.get('assunto')
        nome_professor = request.form.get('nome_professor')

        encontros = encontro_repo.select(
            trilha=trilha,
            data_inicial=data_inicial,
            data_final=data_final,
            hora=hora,
            modulo=modulo,
            assunto=assunto,
            nome_professor=nome_professor
        )

    return render_template('encontros.html', encontros=encontros)

@trilhas_blueprinte.route('/encontros/detalhes/<int:id_encontro>', methods=['GET'])
def ver_detalhes_encontro(id_encontro):
    try:
        # Usando o método 'select' para buscar o encontro pelo 'id_encontro'
        encontro = encontro_repo.select(encontro_id=id_encontro)
        
        # Verifica se o encontro foi encontrado
        if encontro is None:
            return "Encontro não encontrado", 404

        # Chamar a função 'calcular_presenca_encontro' e obter os dados de presença
        lista_presenca = encontro_repo.calcular_presenca_encontro(id_encontro)
        
        # Verificar se lista_presenca é uma lista
        if not isinstance(lista_presenca, list):
            return "Erro: a lista de presença não está no formato esperado", 500
        
        # Renderizar o template passando o encontro e a lista de presença formatada
        return render_template('encontros_detalhes.html', encontro=encontro, lista_presenca=lista_presenca)
    
    except Exception as e:
        # Caso ocorra algum erro ao processar o encontro
        return f"Erro ao processar o encontro: {str(e)}", 500
    
@trilhas_blueprinte.route('/encontros/adicionar', methods=['GET', 'POST'])
def adicionar_encontro():
    error = None
    success_message = None
    professores = professor_repo.listar_todos()
    aspirantes = aspirante_repo.get_all()

    if request.method == 'POST':
        try:
            trilha = request.form['trilha'].strip()
            data = request.form['data']
            hora = request.form['hora']
            modulo = request.form['modulo'].title().strip()
            assunto = request.form['assunto'].title().strip()
            duracao = int(request.form['duracao'].strip())
            id_professor = int(request.form['id_professor'])
            atividade = request.form['atividade'].lower() == 'true'

            # Validar dados do encontro
            error = validar_dados_encontro(trilha, data, hora, modulo, assunto, duracao, id_professor)

            if error:
                return render_template('encontros_adicionar.html', error=error, professores=professores, aspirantes=aspirantes)

            # Coletar a lista de aspirantes e seus minutos
            aspirantes_presentes = []
            for aspirante_id in request.form.getlist('aspirantes[]'):
                minutos = request.form.get(f'minutos_{aspirante_id}')
                if minutos:
                    aspirantes_presentes.append({'id': aspirante_id, 'minutos': minutos})

            # Inserir o encontro no banco de dados
            ultimo_id = encontro_repo.get_last_id()
            novo_id = (ultimo_id + 1) if ultimo_id is not None else 1
            sucesso, mensagem = encontro_repo.add(
                novo_id, trilha, data, hora, modulo, assunto, duracao, id_professor, atividade, aspirantes_presentes
            )

            success_message = mensagem if sucesso else "Erro ao adicionar o encontro."
        except Exception as e:
            error = f"Ocorreu um erro: {str(e)}"

    return render_template('encontros_adicionar.html', 
                        error=error, 
                        success_message=success_message, 
                        professores=professores, 
                        aspirantes=aspirantes)
