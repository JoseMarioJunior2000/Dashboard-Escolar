from flask import Blueprint, render_template, redirect, url_for, flash, request
from services.repository_instances import aspirante_repo, encontro_repo

lista_blueprinte = Blueprint('lista', __name__)

@lista_blueprinte.route('/aspirante/lista') 
def lista_aspirantes():
    aspirantes = aspirante_repo.get_all()  # Supondo que o método existe
    return render_template('aspirantes_lista.html', aspirantes=aspirantes)

@lista_blueprinte.route('/aspirante/<int:id>')
def visualizar_aspirante(id):
    aspirante = aspirante_repo.get_by_id(id)  # Supondo que o método existe
    if not aspirante:
        return "Aspirante não encontrado", 404
    
    # Contabiliza as aulas em que o aspirante esteve presente
    total_aulas, porcentagem_presenca = encontro_repo.count_encontros_por_aspirante(id)

    return render_template('aspirantes_detalhes.html', aspirante=aspirante, 
                           total_aulas=total_aulas, 
                           porcentagem_presenca=porcentagem_presenca)

@lista_blueprinte.route('/aspirante/deletar/<int:id>', methods=['POST'])
def deletar_aspirante(id):
    aspirante = aspirante_repo.get_by_id(id)  # Verifica se o aspirante existe
    if not aspirante:
        flash("Aspirante não encontrado.", "danger")
        return redirect(url_for('lista.lista_aspirantes'))

    try:
        aspirante_repo.delete(id)  # Chama o método delete do repositório
        flash(f"Aspirante '{aspirante.nome}' foi removido com sucesso.", "success")
    except Exception as e:
        flash(f"Erro ao deletar aspirante: {e}", "danger")
    return redirect(url_for('lista.lista_aspirantes'))

@lista_blueprinte.route('/aspirante/alterar_foto/<int:id>', methods=['POST'])
def alterar_foto(id):
    aspirante = aspirante_repo.get_by_id(id)
    if not aspirante:
        flash("Aspirante não encontrado.", "danger")
        return redirect(url_for('lista.lista_aspirantes'))
    
    foto = request.files.get('foto')  # Pega o arquivo enviado
    if foto:
        try:
            # Lê o conteúdo do arquivo e passa para o repositório
            foto_bytes = foto.read()  # Lê o arquivo da foto
            aspirante_repo.update(id, 'foto', foto_bytes)  # Atualiza a foto do aspirante

            flash("Foto alterada com sucesso!", "success")
        except Exception as e:
            flash(f"Erro ao alterar foto: {e}", "danger")
    else:
        flash("Nenhuma foto selecionada.", "warning")
    
    return redirect(url_for('lista.visualizar_aspirante', id=id))