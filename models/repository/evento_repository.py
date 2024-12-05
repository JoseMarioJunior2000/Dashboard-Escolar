from models.configs.connection import DataBaseConnection
from models.entities.eventos import Evento, evento_aspirantes
from models.entities.aspirante import Aspirante  # Import necessário para acessar Aspirante
from sqlalchemy.exc import IntegrityError
from flask import jsonify
from datetime import datetime, timedelta

class EventoRepository:
    """
    Classe responsável por gerenciar operações relacionadas aos eventos no banco de dados.
    """

    def __init__(self, repository: DataBaseConnection):
        """
        Inicializa o repositório com uma instância de conexão com o banco de dados.

        :param repository: Instância de DataBaseConnection que fornece acesso ao banco de dados.
        """
        self.repository = repository

    def add(self, nome, data, hora, aspirante_ids: list):
        """
        Adiciona um novo evento ao banco de dados e associa aspirantes ao evento.

        :param nome: Nome do evento.
        :param data: Data do evento (string no formato "YYYY-MM-DD" ou objeto datetime.date).
        :param hora: Hora do evento (string no formato "HH:MM" ou objeto datetime.time).
        :param aspirante_ids: Lista de IDs dos aspirantes a serem associados ao evento.
        :return: Tupla (bool, str):
                 - True e mensagem de sucesso caso o evento seja adicionado corretamente.
                 - False e mensagem de erro caso ocorra alguma falha.
        """
        with self.repository.get_session() as session:
            try:
                # Converte data e hora para os formatos corretos, se necessário
                if isinstance(data, str):
                    data = datetime.strptime(data, "%Y-%m-%d").date()
                if isinstance(hora, str):
                    hora = datetime.strptime(hora, "%H:%M").time()

                # Cria um novo evento
                novo_evento = Evento(
                    nome=nome,
                    data=data,
                    hora=hora
                )
                session.add(novo_evento)
                session.flush()  # Garante que o ID do evento foi gerado

                # Associa os aspirantes ao evento
                for aspirante_id in aspirante_ids:
                    aspirante = session.get(Aspirante, aspirante_id)
                    if aspirante:
                        novo_evento.aspirantes.append(aspirante)
                    else:
                        return False, "Erro: Nenhum aspirante válido encontrado."

                # Confirma as alterações no banco de dados
                session.commit()
                return True, "Evento adicionado com sucesso."

            except IntegrityError as e:
                # Rollback em caso de erros de integridade referencial
                session.rollback()
                print(f"Erro de integridade ao adicionar evento: {e}")
                return False, "Erro de integridade ao adicionar evento."
            except Exception as e:
                # Rollback para qualquer outro erro
                session.rollback()
                print(f"Erro ao adicionar evento: {e}")
                return False, f"Erro ao adicionar evento: {e}"

    def all_events(self):
        """
        Recupera todos os eventos do banco de dados, incluindo os aspirantes associados.

        :return: Lista de dicionários contendo as informações dos eventos:
                - "nome": Nome do evento.
                - "data": Data do evento no formato "YYYY-MM-DD".
                - "hora": Hora do evento no formato "HH:MM".
                - "events": Lista de dicionários contendo:
                 - "title": Nome do evento.
                 - "time": Hora do evento no formato "HH:MM".
                 - "aspirantes": Lista de nomes dos aspirantes associados.
                Retorna uma lista vazia em caso de falha.
        """
        with self.repository.get_session() as session:
            try:
                # Consulta todos os eventos
                eventos = session.query(Evento).all()
                
                # Função para capitalizar os nomes
                def capitalize_name(name):
                    return ' '.join([word.capitalize() for word in name.split()])

                # Preparar eventos no formato necessário para o JavaScript
                eventos_js = [
                    {
                        "day": evento.data.day,
                        "month": evento.data.month,
                        "year": evento.data.year,
                        "events": [
                            {
                                "title": evento.nome,
                                "time": evento.hora.strftime('%H:%M'),
                                "aspirantes": [capitalize_name(aspirante.nome) for aspirante in evento.aspirantes]                           
                            }
                        ]
                    }
                    for evento in eventos
                ]

                # Retorna a lista de eventos formatada
                return eventos_js

            except Exception as e:
                # Captura e exibe erros
                print(f"Erro ao buscar eventos: {e}")
                return []

    def eventos_da_semana(self):
        with self.repository.get_session() as session:
            try:
                hoje = datetime.today().date()
                sete_dias_depois = hoje + timedelta(days=7)

                # Buscar eventos no intervalo de hoje até sete dias após hoje
                eventos = session.query(Evento).filter(Evento.data >= hoje, Evento.data <= sete_dias_depois).all()
                return eventos
            except Exception as e:
                # Captura e exibe erros
                print(f"Erro ao buscar eventos: {e}")
                return []