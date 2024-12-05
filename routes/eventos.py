from flask import Blueprint, render_template, request, jsonify
from services.repository_instances import aspirante_repo, eventos_repo
from datetime import datetime
from services.validations import converter_data, converter_hora
import json

eventos_blueprint = Blueprint('eventos', __name__)

@eventos_blueprint.route('/eventos/', methods=['GET', 'POST'])
def calendario():
    if request.method == 'GET':
        # Obtendo todos os eventos usando a função all_events
        eventos = eventos_repo.all_events()
        
        # Convertendo os eventos para JSON
        eventos_json = json.dumps(eventos)
        
        # Obtendo todos os aspirantes
        aspirantes = aspirante_repo.get_all()
        
        return render_template('eventos.html',  eventos_json=eventos_json, aspirantes=aspirantes)
    
    if request.method == 'POST':
        # Obtendo os dados enviados em JSON
        data = request.get_json()  # Agora estamos recebendo dados como JSON
        
        nome = data.get('nome')
        data_evento = data.get('data')
        hora = data.get('hora')
        aspirante_ids = data.get('aspirante_ids')  # Lista de IDs
        
        # Exibindo os dados recebidos
        print(f"Dados recebidos para o evento: nome={nome}, data={data_evento}, hora={hora}, aspirante_ids={aspirante_ids}")

        # Verificando se os dados foram corretamente obtidos
        if not nome or not data_evento or not hora:
            print("Erro: Dados faltando no formulário.")
            return jsonify({"success": False, "message": "Dados do evento incompletos."}), 400

        # Converte a data usando a função de conversão
        data_evento_obj = converter_data(data_evento)
        if not data_evento_obj:
            return jsonify({"success": False, "message": "Formato de data inválido. Use o formato YYYY-MM-DD."}), 400

        # Converte a hora usando a função de conversão
        hora_obj = converter_hora(hora)
        if not hora_obj:
            return jsonify({"success": False, "message": "Formato de hora inválido. Use o formato HH:MM."}), 400

        # Chamada ao método de adicionar evento
        sucesso, mensagem = eventos_repo.add(nome, data_evento_obj, hora_obj, aspirante_ids)
        print(f"Resultado da tentativa de adicionar evento: sucesso={sucesso}, mensagem={mensagem}")  # Depuração

        # Retorna uma resposta em JSON
        if sucesso:
            print("Evento adicionado com sucesso.")  # Depuração
            return jsonify({"success": True, "message": mensagem}), 201
        else:
            print(f"Falha ao adicionar evento: {mensagem}")  # Depuração
            return jsonify({"success": False, "message": mensagem}), 400

@eventos_blueprint.route('/get-events', methods=['GET'])
def get_events():
    try:
        eventos = eventos_repo.all_events()
        return jsonify(eventos), 200
    except Exception as e:
        return jsonify({"error": "Erro ao obter eventos"}), 500