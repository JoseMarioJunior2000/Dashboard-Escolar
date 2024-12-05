from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
import os
from services.repository_instances import aspirante_repo, encontro_repo, turma_repo, atividades_repo

# Cria o blueprint para o upload
upload_blueprint = Blueprint('upload', __name__)

def ensure_upload_folder():
    """ Verifica se o diretório de upload existe, se não, cria """
    upload_folder = current_app.config['UPLOAD_FOLDER']
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)

# Função genérica de upload
def upload_excel(repository):
    """ Faz o upload de arquivos Excel (xlsm e xlsx) e processa com o repositório """
    if 'file' not in request.files:
        return jsonify(success=False, message="Nenhum arquivo foi enviado.")

    file = request.files['file']

    # Verifica se o arquivo é do tipo Excel permitido
    if file and file.filename.lower().endswith(('.xlsm', '.xlsx')):
        filename = secure_filename(file.filename)
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)

        # Certifica que o diretório de upload existe e salva o arquivo
        os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
        file.save(file_path)
        print(f"Arquivo salvo em: {file_path}")

        # Usa a instância do repositório passado para processar o arquivo
        success, message = repository.insert_excel(file_path)

        if not success:
            return jsonify(success=False, message=f"Erro ao processar arquivo: {message}"), 500

        return jsonify(success=True, message="Arquivo processado com sucesso!")
    else:
        return jsonify(success=False, message="O arquivo deve estar no formato .xlsm ou .xlsx.")

# Rota para upload de aspirantes
@upload_blueprint.route('/upload_aspirante', methods=['POST'])
def upload_aspirante():
    return upload_excel(aspirante_repo)

# Rota para upload de encontros
@upload_blueprint.route('/upload_encontro', methods=['POST'])
def upload_encontro():
    return upload_excel(encontro_repo)

# Rota para upload de turmas
@upload_blueprint.route('/upload_turma', methods=['POST'])
def upload_turma():
    return upload_excel(turma_repo)

# Rota para upload de atividades
@upload_blueprint.route('/upload_atividades', methods=['POST'])
def upload_atividades():
    return upload_excel(atividades_repo)
