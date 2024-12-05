from flask import Blueprint, render_template, request, redirect, url_for
from services.repository_instances import aspirante_repo, turma_repo
from services.validations import validar_dados_aspirante
from werkzeug.utils import secure_filename
import os

adicionar_blueprinte = Blueprint('adicionar', __name__)

@adicionar_blueprinte.route('/aspirante/adicionar', methods=['GET', 'POST'])
def adicionar_aspirante():
    error = None

    if request.method == 'POST':
        nome = request.form['nome'].upper().strip()
        email = request.form['email'].lower().strip()
        idade = request.form['idade'].strip()
        sexo = request.form['sexo']
        uf = request.form['uf'].upper().strip()
        fone = request.form['fone'].strip()
        ativo = request.form['ativo']
        turma_id = request.form.get('turma')
        foto = request.files.get('foto')
        foto_path = None

        if foto:
            if foto.filename == '':
                error = "Nenhuma foto selecionada."
            elif allowed_file(foto.filename):
                filename = secure_filename(foto.filename)
                foto_path = os.path.join('uploads/aspirantes', filename)
                foto.save(foto_path)
            else:
                error = "O arquivo deve ser uma imagem válida."

        if not error:
            error = validar_dados_aspirante(nome, email, idade, sexo, uf, fone)
        
        if error:
            turmas = turma_repo.select()
            ufs = get_uf_list()
            return render_template('aspirantes_adicionar.html', turmas=turmas, ufs=ufs, error=error)

        ultimo_id = aspirante_repo.get_last_id()
        novo_id = (ultimo_id + 1) if ultimo_id is not None else 1
        aspirante_repo.add(novo_id, nome, email, idade, sexo, uf, fone, ativo, turma_id, foto=foto_path, aspirantld=None)
        
        return redirect(url_for('lista.lista_aspirantes'))

    turmas = turma_repo.select()
    ufs = get_uf_list()
    return render_template('aspirantes_adicionar.html', turmas=turmas, ufs=ufs, error=error)

# Função para verificar se o arquivo tem uma extensão permitida
def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}  # Extensões permitidas
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_uf_list():
    # Lista de siglas dos estados brasileiros
    return [
        "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", 
        "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", 
        "RS", "RO", "RR", "SC", "SP", "SE", "TO"
    ]