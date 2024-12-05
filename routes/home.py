from flask import Blueprint, render_template
from services.repository_instances import aspirante_repo, eventos_repo, turma_repo

home_blueprinte = Blueprint('home', __name__)

@home_blueprinte.route('/')
def home():
    grafico_sexo = aspirante_repo.grafico_genero()
    grafico_idade = aspirante_repo.criar_grafico_faixas_etarias()
    eventos = eventos_repo.eventos_da_semana()
    grafico_turma = turma_repo.gerar_turma_aspirantes_graph()
    return render_template('home.html', grafico_sexo=grafico_sexo, 
                           grafico_idade=grafico_idade, 
                           eventos=eventos, 
                           grafico_turma=grafico_turma)