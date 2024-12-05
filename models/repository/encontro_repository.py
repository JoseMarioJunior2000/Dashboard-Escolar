from models.configs.connection import DataBaseConnection
from models.entities.encontro import Encontro, encontro_aspirantes
from models.entities.professor import Professor
from models.entities.aspirante import Aspirante
import pandas as pd
from flask import jsonify
import os
from sqlalchemy import insert, Date, Integer, String, Boolean, Time, func, insert, delete, update, extract
from datetime import datetime, time
from services.validations import converter_data, converter_hora, encontro_slug
from sqlalchemy.sql import text
import plotly.graph_objs as go
import json

class EncontroRepository:
    def __init__(self, repository: DataBaseConnection):
        self.repository = repository

    def add(self, novo_id, trilha: str, data: str, hora: str, modulo: str, assunto: str, duracao: int, 
                id_professor: int, atividade: bool, aspirantes: list, meetingId=None):
            """
            Adiciona um novo encontro ao banco de dados, incluindo associações com aspirantes e minutos.
            
            :param trilha: Trilha do encontro
            :param data: Data do encontro
            :param hora: Hora do encontro
            :param modulo: Módulo do encontro
            :param assunto: Assunto do encontro (opcional)
            :param duracao: Duração do encontro em minutos
            :param id_professor: ID do professor responsável
            :param atividade: Indica se a atividade está ativa
            :param aspirantes: Lista de dicionários com os IDs dos aspirantes e minutos associados 
                                (ex: [{"id": 1, "minutos": 30}, {"id": 2, "minutos": 45}])
            :param meetingId: ID opcional do meeting
            :return: Tuple (bool, str) indicando sucesso ou falha
            """
            try:
                with self.repository.get_session() as session:  # Criando a sessão
                    # Criar o encontro
                    novo_encontro = Encontro(
                        id= novo_id,
                        trilha=trilha,
                        data=converter_data(data),
                        hora=converter_hora(hora),
                        modulo=modulo,
                        assunto=assunto if assunto else None,
                        duracao=int(duracao),
                        id_professor=int(id_professor),
                        atividade=atividade,
                        meetingId=meetingId
                    )

                    session.add(novo_encontro)  # Adiciona o encontro à sessão
                    session.flush()  # Garante que o ID do encontro esteja disponível após o flush

                    # Agora vamos associar os aspirantes
                    for aspirante in aspirantes:
                        self.associar_aspirante(novo_encontro.id, aspirante['id'], aspirante['minutos'], session)

                    session.commit()  # Comitar todas as alterações feitas
                    return True, "Encontro e associações adicionados com sucesso!"
            
            except Exception as e:
                session.rollback()  # Reverter transações em caso de erro
                print(f"Erro ao inserir o encontro e as associações: {e}")
                return False, f"Erro ao inserir o encontro e as associações: {str(e)}"

    def associar_aspirante(self, encontro_id, aspirante_id, minutos, session):
        try:
            # Inserir a associação do aspirante ao encontro
            query = text("""
                INSERT INTO encontro_aspirantes (encontro_id, aspirante_id, minuto)
                VALUES (:encontro_id, :aspirante_id, :minuto)
            """)
            session.execute(query, {'encontro_id': encontro_id, 'aspirante_id': aspirante_id, 'minuto': minutos})
        except Exception as e:
            session.rollback()  # Reverter transações em caso de erro
            raise e
        
    def insert_excel(self, caminho_arquivo):
        try:
            excel_data = pd.ExcelFile(caminho_arquivo)

            # Verificar se as abas obrigatórias existem
            if 'encontros' not in excel_data.sheet_names or 'encontro_aspirantes' not in excel_data.sheet_names:
                return False, "Erro: o arquivo não contém as abas obrigatórias 'encontros' e/ou 'encontro_aspirantes'."

            df_encontros = pd.read_excel(caminho_arquivo, sheet_name='encontros')
            df_encontro_aspirantes = pd.read_excel(caminho_arquivo, sheet_name='encontro_aspirantes')

            # Colunas obrigatórias
            encontros_cols = {'id', 'trilha', 'data', 'hora', 'modulo', 'assunto', 'duracao', 'id_professor', 'atividade', 'meetingId', 'atualizado'}
            encontro_aspirantes_cols = {'id_encontro', 'id_aspirante', 'minutos'}

            # Verificar colunas obrigatórias
            if not encontros_cols.issubset(df_encontros.columns) or not encontro_aspirantes_cols.issubset(df_encontro_aspirantes.columns):
                return False, "Erro: verifique as colunas obrigatórias nas abas 'encontros' ou 'encontro_aspirantes'."

            errors = []
            with self.repository.get_session() as session:
                for _, row in df_encontros.iterrows():
                    atualizado = int(row['atualizado'])  # Verifica o valor da coluna 'atualizado'

                    if atualizado == 1:  # Inserir
                        result = self.add_excel(row, session)
                    elif atualizado == 2:  # Atualizar
                        result = self.update_excel(row, session)
                    elif atualizado == 3:  # Deletar
                        result = self.delete_excel(row, session)
                    else:
                        result = False, f"Erro: Valor inválido na coluna 'atualizado' para o ID {row['id']}."

                    if not result[0]:
                        # Faz um flush para garantir que todos os encontros foram "empurrados"
                        errors.append(result[1])

                # Faz um flush para garantir que todos os encontros foram "empurrados"
                if not errors:
                    session.flush()

                self.insert_associacoes(session, df_encontro_aspirantes)

                # Confirmar as transações ao final
                if not errors:
                    session.commit()
                    return True, "Processo concluído com sucesso!"
                else:
                    session.rollback()
                    return False, f"Erros encontrados: {', '.join(errors)}"

        except Exception as e:
            return False, f"Erro ao processar o arquivo: {str(e)}"
        
    def insert_associacoes(self, session, df_encontro_aspirantes):
        """Insere as associações de aspirantes aos encontros."""
        associações_para_inserir = []
        for _, row in df_encontro_aspirantes.iterrows():
            stmt = insert(encontro_aspirantes).values(
                encontro_id=row['id_encontro'],
                aspirante_id=row['id_aspirante'],
                minuto=row['minutos']
            )
            associações_para_inserir.append(stmt)

        for stmt in associações_para_inserir:
            session.execute(stmt)
        return True, "Associações de aspirantes inseridas com sucesso."
    
    def add_excel(self, row, session):
        try:
            novo_encontro = Encontro(
                id=int(row['id']),
                trilha=row['trilha'],
                data=converter_data(row['data']),
                hora=converter_hora(row['hora']),
                modulo=row['modulo'],
                assunto=row['assunto'] if not pd.isna(row['assunto']) else None,
                duracao=int(row['duracao']),
                id_professor=int(row['id_professor']),
                atividade=bool(row['atividade']),
                meetingId=int(row['meetingId']) if not pd.isna(row['meetingId']) else None
            )
            session.add(novo_encontro)
            return True, f"Encontro ID {row['id']} inserido com sucesso."
        except Exception as e:
            return False, f"Erro ao inserir o Encontro ID {row['id']}: {e}"
        
    def update_excel(self, row, session):
        """Atualiza um encontro existente no banco de dados."""
        try:
            encontro_id = int(row['id'])

            stmt = (
                update(Encontro).
                where(Encontro.id == encontro_id).
                values(
                    trilha=row['trilha'],
                    data=converter_data(row['data']),
                    hora=converter_hora(row['hora']),
                    modulo=row['modulo'],
                    assunto=row['assunto'] if not pd.isna(row['assunto']) else None,
                    duracao=int(row['duracao']),
                    id_professor=int(row['id_professor']),
                    atividade=True if row['atividade'] == 1 else False,
                    meetingId=int(row['meetingId']) if not pd.isna(row['meetingId']) else None
                )
            )

            session.execute(stmt)
            return True, f"Encontro ID {row['id']} atualizado com sucesso."
        except Exception as e:
            return False, f"Erro ao atualizar o Encontro ID {row['id']}: {e}"
        
    def delete_excel(self, session, row):
        """Deleta um encontro existente no banco de dados."""
        try:
            encontro_id = int(row['id'])

            stmt = delete(Encontro).where(Encontro.id == encontro_id)
            session.execute(stmt)
            return True, f"Encontro {encontro_id} deletado com sucesso."
        except Exception as e:
            return False, f"Erro ao deletar o Encontro ID {row['id']}: {e}"

    def select(self, trilha=None, data_inicial=None, data_final=None, hora=None, modulo=None, assunto=None, nome_professor=None, encontro_id=None):
        with self.repository.get_session() as session:
            query = session.query(Encontro).join(Professor)

            if encontro_id is not None:  # Adicionando essa verificação
                return query.filter(Encontro.id == encontro_id).one_or_none()  # Retorna um único encontro ou None

            if trilha:
                query = query.filter(Encontro.trilha == trilha)
            if data_inicial:
                data_inicial = datetime.strptime(data_inicial, '%Y-%m-%d').date()
                query = query.filter(Encontro.data >= data_inicial)
            if data_final:
                data_final = datetime.strptime(data_final, '%Y-%m-%d').date()
                query = query.filter(Encontro.data <= data_final)
            if hora:
                hora = datetime.strptime(hora, '%H:%M').time()
                query = query.filter(Encontro.hora == hora)
            if modulo:
                query = query.filter(Encontro.modulo.like(f"%{modulo}%"))
            if assunto:
                query = query.filter(Encontro.assunto.like(f"%{assunto}%"))
            if nome_professor:
                query = query.filter(Professor.nome.like(f"%{nome_professor}%"))

            encontros_filtrados = query.all()

            # Garantir que encontros_filtrados seja sempre uma lista (mesmo vazia)
            if not encontros_filtrados:
                encontros_filtrados = []

            return encontros_filtrados

            
    def update(self):
        with self.repository.get_session() as session:
            try:
                # Solicita o ID do encontro que deseja atualizar
                encontro_id = input('Digite o ID do encontro que deseja atualizar: ')
                encontro = session.query(Encontro).filter_by(id=encontro_id).first()

                # Verifica se o encontro foi encontrado
                if encontro:
                    print(f"Encontro encontrado: {encontro}")

                    # Solicita a coluna que deseja modificar
                    coluna_nome = input("Digite o nome da coluna que deseja modificar: ").strip().lower()
                    
                    # Verifica se o encontro tem o atributo solicitado
                    if not hasattr(encontro, coluna_nome):
                        raise Exception(f"A coluna '{coluna_nome}' não existe na tabela.")

                    # Solicita o novo valor para a coluna
                    novo_valor = input(f"Digite o novo valor para a coluna '{coluna_nome}': ")

                    coluna_atributo = getattr(Encontro, coluna_nome)  # Pegando a definição da coluna

                    if isinstance(coluna_atributo.type, Time):
                        try:
                            # Convertendo a string para um objeto datetime.time
                            novo_valor = datetime.strptime(novo_valor, '%H:%M').time()
                        except ValueError:
                            raise ValueError("Formato de hora inválido. Use o formato 'HH:MM'.")

                    # Verifica o tipo da coluna e faz a conversão correta do valor
                    elif isinstance(coluna_atributo.type, Date):
                        try:
                            # Convertendo a string para um objeto datetime.date
                            novo_valor = datetime.strptime(novo_valor, '%d/%m/%Y').date()
                        except ValueError:
                            raise ValueError("Formato de data inválido. Use o formato 'DD/MM/YYYY'.")

                    elif isinstance(coluna_atributo.type, Integer):
                        # Normaliza o input para um valor inteiro
                        try:
                            novo_valor = int(novo_valor)
                        except ValueError:
                            raise ValueError("O valor fornecido não é um número inteiro válido.")

                    elif isinstance(coluna_atributo.type, String):
                        # Normaliza o input para um valor string
                        novo_valor = str(novo_valor)

                    elif isinstance(coluna_atributo.type, Boolean):
                        # Normaliza o input para um valor booleano
                        novo_valor = novo_valor.lower() in ['true', '1', 't', 'y', 'yes']

                    # Atualiza o valor da coluna no objeto encontro
                    setattr(encontro, coluna_nome, novo_valor)

                    # Atualiza no banco de dados
                    session.commit()
                    print(f"Encontro '{encontro_id}' atualizado com sucesso.")
                else:
                    print(f"Encontro com ID '{encontro_id}' não encontrado.")

            except ValueError:
                print("Erro: Valor inválido fornecido. Certifique-se de que o novo valor corresponde ao tipo de dados esperado.")
            except Exception as e:
                session.rollback()
                print(f"Erro ao atualizar encontro: {e}")

    def delete(self):
        with self.repository.get_session() as session:
            try:
                encontro_id = input('Digite o ID do encontro que deseja remover: ')
                encontro = session.query(Encontro).filter_by(id=encontro_id).first()

                if encontro:
                    confirmacao = input(f"Tem certeza que deseja remover o encontro '{encontro.id}'? (S/N): ").strip().lower()
                    if confirmacao == 's':
                        session.delete(encontro)
                        session.commit()
                        print(f"Encontro '{encontro.id}' removido com sucesso.")
                    else:
                        print(f"Remoção do encontro '{encontro.id}' cancelada.")
                else:
                    print(f"Encontro com nome '{encontro_id}' não encontrado.")
            except Exception as e:
                session.rollback()
                print(f"Erro ao remover encontro: {e}")   
        
    def calcular_presenca_encontro(self, id_encontro):
        with self.repository.get_session() as session:
            try:
                encontro = session.query(Encontro).filter(Encontro.id == id_encontro).first()

                if not encontro:
                    print("Encontro não encontrado.")
                    return None

                duracao_aula = encontro.duracao

                resultados = session.query(
                    Aspirante.nome,
                    encontro_aspirantes.c.minuto
                ).join(encontro_aspirantes, Aspirante.id == encontro_aspirantes.c.aspirante_id).filter(
                    encontro_aspirantes.c.encontro_id == id_encontro
                ).all()

                lista_presenca = []

                for aspirante_nome, minutos_presentes in resultados:
                    if minutos_presentes >= duracao_aula:
                        porcentagem_presenca = 100  
                    else:
                        porcentagem_presenca = (minutos_presentes / duracao_aula) * 100

                    # Verifica se a porcentagem de presença é 75% ou mais
                    presenca = True if porcentagem_presenca >= 75 else False

                    lista_presenca.append({
                        'Aspirante': aspirante_nome,
                        'Minutos Presentes': minutos_presentes,
                        'Duração da Aula': duracao_aula,
                        'Porcentagem de Presença': f"{porcentagem_presenca:.2f}%",
                        'Presença': presenca  # Adiciona a verificação de presença
                    })

                # Convert the list to a DataFrame and print it for debugging
                df_presenca = pd.DataFrame(lista_presenca)

                # Convert the DataFrame to a list of dictionaries before returning it
                return df_presenca.to_dict(orient='records')  # Convert to a list of dicts

            except Exception as e:
                print(f"Erro ao calcular a presença: {e}")
                return []  # Return an empty list in case of error

    def get_last_id(self):
        with self.repository.get_session() as session:
            return session.query(func.max(Encontro.id)).scalar()
        
    def get_by_slug(self, slug):
        """Busca o encontro pelo slug gerado."""
        encontros = self.select()  # Retorna todas as turmas cadastradas
        for encontro in encontros:
            if encontro_slug(encontro.id) == slug:
                return encontro
        return None
        
    def count_encontros_por_aspirante(self, aspirante_id: int):
        """
        Conta o número de encontros que um aspirante participou com presença de 75% ou mais e a porcentagem de presença.

        :param aspirante_id: ID do aspirante que desejamos contar os encontros.
        :return: Número de encontros que o aspirante participou com 75% ou mais de presença, e a porcentagem de presença.
        """
        try:
            with self.repository.get_session() as session:
                # Recupera os encontros associados ao aspirante na tabela de associação encontro_aspirantes
                encontros_aspirante = session.query(encontro_aspirantes).filter(
                    encontro_aspirantes.c.aspirante_id == aspirante_id
                ).all()

                # Total de encontros e contador de aulas com presença >= 75%
                total_aulas = 0
                total_encontros = len(encontros_aspirante)

                for encontro_aspirante in encontros_aspirante:
                    # Recupera o encontro correspondente usando o ID
                    encontro = session.query(Encontro).filter(Encontro.id == encontro_aspirante.encontro_id).first()

                    if encontro:
                        # Verifica se o aspirante esteve presente por 75% ou mais do tempo do encontro
                        if encontro_aspirante.minuto >= (0.75 * encontro.duracao):
                            total_aulas += 1

                # Calcula a porcentagem de presença
                porcentagem_presenca = 0
                if total_encontros > 0:
                    porcentagem_presenca = (total_aulas / total_encontros) * 100

                return total_aulas, porcentagem_presenca

        except Exception as e:
            print(f"Erro ao contar encontros: {e}")
            return 0, 0
        
    def count_aulas(self):
        try:
            with self.repository.get_session() as session:
                total = session.query(Encontro).filter(Encontro.trilha != "ME").count()
                return total
        except Exception as e:
            print(f"Erro ao contar todos os encontros: {e}")
            return None
        
    def grafico_aulas_professor(self, ano=None, mes=None):
        try:
            with self.repository.get_session() as session:
                # Inicia a consulta básica
                query = session.query(
                    Professor.nome.label('professor_nome'),
                    Encontro.trilha,
                    func.count(Encontro.id).label('total_aulas')
                ).join(Professor, Professor.id == Encontro.id_professor) \
                .group_by(Professor.nome, Encontro.trilha)

                # Aplica o filtro de ano se fornecido
                if ano:
                    query = query.filter(extract('year', Encontro.data) == ano)

                if mes:
                    query = query.filter(extract('month', Encontro.data) == mes)

                # Exclui a trilha "ME"
                query = query.filter(Encontro.trilha != 'ME')

                # Executa a consulta
                results = query.all()

                # Gera o gráfico a partir dos resultados
                return self.gerar_grafico_professor_aula(results)

        except Exception as e:
            print(f"Erro ao contar aulas por professor: {e}")
            return json.dumps({'error': 'Erro ao contar aulas por professor'})

    def gerar_grafico_professor_aula(self, results):
        try:
            if not results:
                return json.dumps({'error': 'Nenhum dado encontrado'})

            # Agrupa os dados por trilha
            trilhas = list(set(item.trilha for item in results))
            traces = []

            for trilha in trilhas:
                # Filtra os dados para cada trilha
                data_filtrada = [item for item in results if item.trilha == trilha]

                # Adiciona o trace para cada trilha
                traces.append(go.Bar(
                    x=[item.professor_nome for item in data_filtrada],
                    y=[item.total_aulas for item in data_filtrada],
                    name=trilha
                ))

            # Layout do gráfico
            layout = go.Layout(
                title='Aulas por Professor',
                xaxis=dict(title='Professores'),
                yaxis=dict(title='Total de Aulas'),
                barmode='group',
                xaxis_tickangle=-45,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                autosize=True,  # Torna o gráfico ajustável
                margin=dict(t=30, l=20, r=20, b=20)  # Ajusta margens conforme necessário
            )

            # Converte o gráfico para JSON
            figura = go.Figure(data=traces, layout=layout)
            return figura.to_json()

        except Exception as e:
            print(f"Erro ao gerar gráfico: {e}")
            return json.dumps({'error': 'Erro ao gerar gráfico'})

    def grafico_minutos_professor(self, ano=None, mes=None):
        try:
            with self.repository.get_session() as session:
                # Consulta para calcular minutos por professor
                query = session.query(
                    Professor.nome.label('professor_nome'),
                    Encontro.trilha,
                    func.sum(Encontro.duracao).label('total_minutos')
                ).join(Professor, Professor.id == Encontro.id_professor) \
                .group_by(Professor.nome, Encontro.trilha)

                # Filtros de ano e mês
                if ano:
                    query = query.filter(extract('year', Encontro.data) == ano)
                if mes:
                    query = query.filter(extract('month', Encontro.data) == mes)

                # Exclui a trilha "ME"
                query = query.filter(Encontro.trilha != 'ME')

                # Executa a consulta
                results = query.all()

                # Gera o gráfico a partir dos resultados
                return self.gerar_grafico_minutos_professor(results)

        except Exception as e:
            print(f"Erro ao gerar gráfico de minutos por professor: {e}")
            return json.dumps({'error': 'Erro ao gerar gráfico de minutos por professor'})
    
    def gerar_grafico_minutos_professor(self, results):
        try:
            if not results:
                return json.dumps({'error': 'Nenhum dado encontrado'})

            # Agrupa os dados por trilha
            trilhas = list(set(item.trilha for item in results))
            traces = []

            for trilha in trilhas:
                # Filtra os dados para cada trilha
                data_filtrada = [item for item in results if item.trilha == trilha]

                # Adiciona o trace para cada trilha
                traces.append(go.Bar(
                    x=[item.professor_nome for item in data_filtrada],
                    y=[item.total_minutos for item in data_filtrada],
                    name=trilha
                ))

            # Layout do gráfico
            layout = go.Layout(
                title='Minutos por Professor',
                xaxis=dict(title='Professores'),
                yaxis=dict(title='Total de Minutos'),
                barmode='group',
                xaxis_tickangle=-45,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )

            # Converte o gráfico para JSON
            figura = go.Figure(data=traces, layout=layout)
            return figura.to_json()

        except Exception as e:
            print(f"Erro ao gerar gráfico: {e}")
            return json.dumps({'error': 'Erro ao gerar gráfico'})
