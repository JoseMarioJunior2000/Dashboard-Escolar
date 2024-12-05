from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
import os
from services.repository_instances import aspirante_repo
# Cria o blueprint para o upload
aspirante_upload_blueprint = Blueprint('aspirante_upload', __name__)

def ensure_upload_folder():
    """ Verifica se o diretório de upload existe, se não, cria """
    upload_folder = current_app.config['UPLOAD_FOLDER']
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)

@aspirante_upload_blueprint.route('/upload_xlsm', methods=['POST'])
def upload_xlsm():
    if 'xlsm_file' not in request.files:
        return jsonify(success=False, message="Nenhum arquivo foi enviado.")
    
    file = request.files['xlsm_file']

    if file and file.filename.endswith('.xlsm'):
        filename = secure_filename(file.filename)
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)

        ensure_upload_folder()
        file.save(file_path)

        aspirante_response = aspirante_repo.insert_excel(file_path)
        if not aspirante_response[0]:
            return jsonify(success=False, message=f"Erro ao processar aspirantes: {aspirante_response[1]}"), 500

        return jsonify(success=True, message="Arquivo processado com sucesso!")
    
    else:
        return jsonify(success=False, message="O arquivo deve ser no formato .xlsm.")
