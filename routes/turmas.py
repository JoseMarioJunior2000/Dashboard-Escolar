from flask import Blueprint, render_template, request, redirect, url_for
from services.repository_instances import turma_repo, aspirante_repo, encontro_repo
from services.validations import validar_dados_turma, turma_slug
from werkzeug.utils import secure_filename
import os

turmas_blueprint = Blueprint('turmas', __name__)

@turmas_blueprint.route('/turmas/adicionar', methods=['GET', 'POST'])
def adicionar_turmas():
    """Adiciona uma nova turma ao banco de dados"""

    error = None
    success_message = None

    if request.method == 'POST':
        try:
            # Capturar os dados enviados pelo formulário
            nome = request.form.get('nome', '').upper().strip()
            data_input = request.form.get('data', '').strip()
            processo = request.form.get('processo', '').strip()

            # Validar dados da turma
            validation_error = validar_dados_turma(nome, data_input, processo)
            if validation_error:
                error = f"Erro de validação: {validation_error}"
                return render_template('turmas_adicionar.html', error=error)

            # Tentar adicionar a turma ao banco de dados
            ultimo_id = turma_repo.get_last_id()
            novo_id = (ultimo_id + 1) if ultimo_id is not None else 1
            sucesso, mensagem = turma_repo.add(novo_id, nome, data_input, processo)

            if sucesso:
                success_message = f"Turma adicionada com sucesso: {mensagem}"
            else:
                error = f"Erro ao adicionar a turma: {mensagem}"

        except KeyError as e:
            error = f"Campo obrigatório ausente: {str(e)}"
        except ValueError as e:
            error = f"Erro de valor inválido: {str(e)}"
        except Exception as e:
            error = f"Ocorreu um erro inesperado: {str(e)}"

    # Renderizar o template com as mensagens de sucesso ou erro
    return render_template('turmas_adicionar.html', error=error, success_message=success_message)

@turmas_blueprint.route('/turmas')
def listar_turmas():
    """Lista as turmas com links baseados no slug."""
    turmas = turma_repo.select()
    turmas_com_slugs = [{"id": t.id, "slug": turma_slug(t.id), "nome": t.nome} for t in turmas]
    return render_template('turmas_detalhes.html', turmas=turmas_com_slugs)

@turmas_blueprint.route('/turmas/<slug>')
def listar_aspirantes_turma(slug):
    """Exibe os aspirantes da turma identificada pelo slug."""
    turma = turma_repo.get_by_slug(slug)
    if not turma:
        return redirect(url_for('turmas.listar_turmas'))  # Redireciona se a turma não for encontrada

    aspirantes = turma_repo._ver_alunos_turma(turma_id=turma.id) or []
    return render_template('aspirantes_turma.html', turma=turma, aspirantes=aspirantes)