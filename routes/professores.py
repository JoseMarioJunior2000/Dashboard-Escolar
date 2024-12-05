from flask import Blueprint, render_template, request
from services.repository_instances import encontro_repo, professor_repo

professores_blueprint = Blueprint('professores', __name__)

@professores_blueprint.route('/professores', methods=['GET'])
def dashboard():
    ano = request.args.get('ano', type=int)
    mes = request.args.get('mes', type=int)

    total_aulas = encontro_repo.count_aulas()
    total_professores = professor_repo.count_professores()

    # Gráficos
    grafico_aulas_json = encontro_repo.grafico_aulas_professor(ano, mes)
    grafico_minutos_json = encontro_repo.grafico_minutos_professor(ano, mes)

    return render_template(
        'professores.html',
        total_aulas=total_aulas,
        total_professores=total_professores,
        grafico_aulas_json=grafico_aulas_json,
        grafico_minutos_json=grafico_minutos_json
    )
