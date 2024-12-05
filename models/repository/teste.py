from datetime import datetime
import pandas as pd
from sqlalchemy import and_
from models.entities.aspirante import Aspirante
from models.entities.encontro import Encontro, encontro_aspirantes
from models.configs.connection import DataBaseConnection

class Teste():
    def __init__(self, repository: DataBaseConnection):
        self.repository = repository

    def select(self):
        nome_aspirante = input('Digite o nome do aspirante: ')
        aspirante_id = self.buscar_id_aspirante(nome_aspirante)

        if not aspirante_id:
            print("Aspirante não encontrado.")
            return

        # Definindo os nomes das trilhas
        trilhas = ['Hard', 'Soft', 'Inglês', 'ME']

        data_inicial = input('Digite a data inicial (YYYY-MM-DD): ')
        data_final = input('Digite a data final (YYYY-MM-DD): ')

        # Inicializando contadores para o número de presenças em cada trilha
        total_presencas = {trilha: 0 for trilha in trilhas}

        for trilha in trilhas:
            presencas_df, total_encontros = self.calcular_presenca_por_trilha(trilha, data_inicial, data_final, aspirante_id)
            
            if not presencas_df.empty:  # Verifica se o DataFrame não está vazio
                print(f"\nTotal de encontros na trilha '{trilha}': {total_encontros}")
                print(presencas_df)  # Exibe o DataFrame
                total_presencas[trilha] = presencas_df['Encontros Presentes'].sum()
            else:
                print(f"Nenhuma presença registrada na trilha '{trilha}'.")

        # Exibir o número total de presenças nas quatro trilhas
        print("\nTotal de presenças por trilha:")
        for trilha, presencas in total_presencas.items():
            print(f"Trilha '{trilha}': {presencas} presenças")

    def buscar_id_aspirante(self, nome_aspirante):
        with self.repository.get_session() as session:
            try:
                aspirante = session.query(Aspirante).filter(Aspirante.nome == nome_aspirante).first()
                if aspirante:
                    return aspirante.id
                else:
                    print(f"Aspirante com nome {nome_aspirante} não encontrado.")
                    return None
            except Exception as e:
                print(f"Erro ao buscar aspirante: {e}")
                return None

    def calcular_presenca_por_trilha(self, trilha, data_inicial, data_final, aspirante_id):
        with self.repository.get_session() as session:
            try:
                # Convertendo as datas para o formato correto
                data_inicial = datetime.strptime(data_inicial, '%Y-%m-%d').date()
                data_final = datetime.strptime(data_final, '%Y-%m-%d').date()

                # Realizar uma junção explícita entre Encontro e encontro_aspirantes
                registros_presenca = session.query(encontro_aspirantes, Encontro).join(
                    Encontro, encontro_aspirantes.c.encontro_id == Encontro.id
                ).filter(
                    and_(
                        encontro_aspirantes.c.aspirante_id == aspirante_id,
                        Encontro.data >= data_inicial,
                        Encontro.data <= data_final
                    )
                ).all()

                if not registros_presenca:
                    print(f"Nenhuma presença registrada para a trilha '{trilha}' no período entre {data_inicial} e {data_final}.")
                    return pd.DataFrame(), 0

                # Inicializa variáveis de contagem
                encontros_presentes = 0
                total_encontros = 0

                # Verificando os registros retornados
                print(f"Total de registros encontrados: {len(registros_presenca)}")
                for registro in registros_presenca:
                    print(f"Registro encontrado: {registro}")  # Verificando o que está sendo retornado

                # Iterar sobre os registros de presença
                for registro in registros_presenca:
                    # Supondo que o registro seja uma tupla com (id_aspirante, id_encontro, ... outros campos)
                    encontro_aspirante_id = registro[0].id  # Pegando o ID da tabela 'encontro_aspirantes'
                    encontro_id = registro[1].id  # Pegando o ID da tabela 'Encontro'

                    # Aqui você pode buscar os dados do encontro aspirante e do encontro
                    encontro_aspirante = session.query(encontro_aspirantes).filter(encontro_aspirantes.c.id == encontro_aspirante_id).first()
                    encontro = session.query(Encontro).filter(Encontro.id == encontro_id).first()

                    if encontro_aspirante and encontro:
                        tempo_presente = encontro_aspirante.minuto  # Agora isso deve funcionar
                        duracao_encontro = encontro.duracao  # Ajuste se necessário

                        if (tempo_presente / duracao_encontro) >= 0.75:  # Conta como presente
                            encontros_presentes += 1

                        total_encontros += 1
                        porcentagem_presenca = (encontros_presentes/total_encontros) * 100
                    else:
                        print(f"Encontro ou encontro aspirante não encontrado para os IDs: {encontro_aspirante_id}, {encontro_id}")

                # Criando o DataFrame
                df_presencas = pd.DataFrame({
                    'Trilha': [trilha],
                    'Encontros Presentes': [encontros_presentes],
                    'Total de Encontros': [total_encontros],
                    'Porcentagem de Presença': [f"{porcentagem_presenca:.2f}%"]
                })

                return df_presencas, total_encontros

            except Exception as e:
                print(f"Erro ao calcular a presença: {e}")
                return pd.DataFrame(), 0  # Retorna DataFrame vazio e zero encontros em caso de erro


