from flask import request
from services.repository_instances import aspirante_repo, professor_repo, turma_repo

def inject_totals():
    if request.endpoint == 'home.home':
        total_aspirantes = aspirante_repo.count_aspirantes()
        total_professores = professor_repo.count_professores()
        total_turmas = turma_repo.count_turmas()
        return {
            'total_aspirantes': total_aspirantes,
            'total_professores': total_professores,
            'total_turmas': total_turmas,
        }
    return {}