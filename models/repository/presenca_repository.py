from models.configs.connection import DataBaseConnection
from models.entities.encontro import Encontro, encontro_aspirantes
import pandas as pd
from sqlalchemy import and_
from datetime import datetime
from models.entities.turma import Turma
from models.entities.aspirante import turmas_aspirantes, Aspirante

class PresencaRepository:
    def __init__(self, repository: DataBaseConnection):
        self.repository = repository

    def select(self):
        nome_turma = input('Digite o nome da turma: ')
        turma_id = self.buscar_turma_por_nome(nome_turma)
        
        if turma_id:
            aspirantes = self.buscar_aspirantes_por_turma(turma_id)
            if aspirantes:
                trilha = input('Digite a trilha: ')  # Solicita a trilha
                data_inicial = input('Digite a data inicial (YYYY-MM-DD): ')
                data_final = input('Digite a data final (YYYY-MM-DD): ')
                presencas_df, total_encontros = self.calcular_presenca_por_trilha(trilha, data_inicial, data_final, aspirantes)
                
                if not presencas_df.empty:  # Verifica se o DataFrame não está vazio
                    print(f"\nTotal de encontros na trilha '{trilha}': {total_encontros}")
                    print(presencas_df)  # Exibe o DataFrame
                else:
                    print("Nenhuma presença registrada.")
            else:
                print("Nenhum aspirante encontrado para a turma.")
        else:
            print("Turma não encontrada.")

    def buscar_turma_por_nome(self, nome_turma):
        with self.repository.get_session() as session:
            try:
                turma = session.query(Turma).filter(Turma.nome == nome_turma).first()
                if turma:
                    return turma.id
                else:
                    print(f"Turma com nome {nome_turma} não encontrada.")
                    return None
            except Exception as e:
                print(f"Erro ao buscar turma: {e}")
                return None

    def buscar_aspirantes_por_turma(self, turma_id):
        with self.repository.get_session() as session:
            try:
                aspirantes = session.query(Aspirante).join(turmas_aspirantes).filter(turmas_aspirantes.c.turma_id == turma_id).all()
                if aspirantes:
                    return aspirantes
                else:
                    print("Nenhum aspirante encontrado para esta turma.")
                    return []
            except Exception as e:
                print(f"Erro ao buscar aspirantes: {e}")
                return []

    def calcular_presenca_por_trilha(self, trilha, data_inicial, data_final, aspirantes):
        with self.repository.get_session() as session:
            try:
                # Convertendo as datas para o formato correto
                data_inicial = datetime.strptime(data_inicial, '%Y-%m-%d').date()
                data_final = datetime.strptime(data_final, '%Y-%m-%d').date()

                # Obtém os IDs dos aspirantes
                aspirante_ids = [aspirante.id for aspirante in aspirantes]
                if not aspirante_ids:
                    print("Nenhum aspirante encontrado para a turma.")
                    return pd.DataFrame(), 0  # Retorna DataFrame vazio e zero encontros

                # Busca encontros que atendem aos critérios especificados
                encontros = session.query(Encontro).filter(
                    and_(
                        Encontro.trilha == trilha,
                        Encontro.data >= data_inicial,
                        Encontro.data <= data_final
                    )
                ).all()

                total_encontros = len(encontros)  # Conta o total de encontros encontrados

                if total_encontros == 0:
                    print(f"Nenhum encontro encontrado para a trilha '{trilha}' entre {data_inicial} e {data_final}.")
                    return pd.DataFrame(), total_encontros  # Retorna DataFrame vazio e zero encontros

                # Dicionário para contar presenças
                presencas = {aspirante.id: {'nome': aspirante.nome, 'encontros_presentes': 0, 'total_encontros': 0} for aspirante in aspirantes}

                # Verifica presença dos aspirantes em cada encontro
                for encontro in encontros:
                    for aspirante in encontro.aspirantes:
                        if aspirante.id in aspirante_ids:
                            # Obtém o registro da presença
                            registro = session.query(encontro_aspirantes).filter(
                                and_(
                                    encontro_aspirantes.c.encontro_id == encontro.id,
                                    encontro_aspirantes.c.aspirante_id == aspirante.id
                                )
                            ).first()
                            if registro:
                                # Verifica se o tempo de presença é maior ou igual a 75% da duração
                                tempo_presente = registro.minuto
                                duracao_encontro = encontro.duracao
                                if (tempo_presente / duracao_encontro) >= 0.75:  # Se 75% ou mais, conta como presente
                                    presencas[aspirante.id]['encontros_presentes'] += 1
                                
                                # Incrementa o total de encontros independentemente
                                presencas[aspirante.id]['total_encontros'] += 1

                # Criação do DataFrame para retorno
                lista_presenca = []
                for aspirante_id, dados in presencas.items():
                    if dados['total_encontros'] > 0:
                        # Cálculo da porcentagem de presença
                        porcentagem_presenca = (dados['encontros_presentes'] / dados['total_encontros']) * 100
                    else:
                        porcentagem_presenca = 0

                    lista_presenca.append({
                        'Aspirante': dados['nome'],
                        'Encontros Presentes': dados['encontros_presentes'],
                        'Total de Encontros': dados['total_encontros'],
                        'Porcentagem de Presença': f"{porcentagem_presenca:.2f}%"
                    })

                df_presencas = pd.DataFrame(lista_presenca)
                return df_presencas, total_encontros  # Retorna DataFrame e total de encontros

            except Exception as e:
                print(f"Erro ao calcular a presença: {e}")
                return pd.DataFrame(), 0  # Retorna DataFrame vazio e zero encontros em caso de erro