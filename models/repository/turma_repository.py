from models.configs.connection import DataBaseConnection
from models.entities.turma import Turma
from datetime import datetime
from sqlalchemy import Date, Integer, String, func
from sqlalchemy.orm import joinedload
import pandas as pd
from services.validations import foto_to_base64, turma_slug, converter_data
import json
from plotly.graph_objs import Bar, Layout, Figure

class TurmaRepository:
    def __init__(self, repository: DataBaseConnection):
        self.repository = repository

    def add(self, id: int, nome: str, data: str, processo: int):
        """
        Adiciona uma nova turma ao banco de dados.

        Parâmetros:
        - id (int): Identificador único da turma.
        - nome (str): Nome da turma.
        - data (datetime): Data associada à turma.
        - processo (int): Número do processo relacionado à turma.

        Retorna:
        tuple: (bool, str)
            - (True, mensagem de sucesso): Caso a turma seja cadastrada com sucesso.
            - (False, mensagem de erro): Caso ocorra um erro durante a inserção.

        Comportamento:
        - Cria uma nova instância da entidade `Turma` com os valores fornecidos.
        - Tenta inserir a nova turma no banco de dados.
        - Realiza o `commit` da transação se a inserção for bem-sucedida.
        - Em caso de erro, reverte a transação com `session.rollback()` e retorna uma mensagem detalhada sobre o erro.

        Exceções tratadas:
        - Qualquer erro gerado durante o processo de inserção, como violação de integridade do banco ou erro de conexão.

        Exemplo de Uso:
        >>> resultado, mensagem = add(1, "Turma A", datetime(2024, 11, 21), 12345)
        >>> print(mensagem)
        "Turma cadastrada com sucesso!"
        """
        with self.repository.get_session() as session:
            try:
                # Cria uma nova instância de Turma
                nova_turma = Turma(id=id, 
                                   nome=nome, 
                                   data=converter_data(data),
                                   processo=processo)

                # Adiciona a turma ao banco
                session.add(nova_turma)
                session.commit()
                return True, "Turma cadastrada com sucesso!"
            
            except Exception as e:
                # Reverte a transação em caso de erro
                session.rollback()
                return False, f"Erro ao inserir turma: {e}"
        
    def insert_excel(self, caminho_arquivo):
        """
        Insere dados de turmas a partir de um arquivo Excel no banco de dados.

        Parâmetros:
        caminho_arquivo (str): Caminho para o arquivo Excel contendo os dados das turmas.

        Retorna:
        tuple: (bool, str)
            - True e mensagem de sucesso caso todas as turmas sejam inseridas corretamente.
            - False e mensagem de erro caso ocorra algum problema.
        """
        try:
            # Lê o arquivo Excel
            excel_data = pd.ExcelFile(caminho_arquivo)

            # Verifica se a aba obrigatória 'turmas' está presente
            if 'turmas' not in excel_data.sheet_names:
                return False, "Erro: o arquivo não contém a aba obrigatória 'turmas'!"

            # Lendo o Excel, planilha 'turmas'
            df_turmas = pd.read_excel(caminho_arquivo, sheet_name='turmas')

            # Colunas obrigatórias
            turmas_cols = {'id', 'nome', 'data', 'processo'}
            if not turmas_cols.issubset(df_turmas.columns):
                return False, "Erro: verifique as colunas obrigatórias: 'id', 'nome', 'data', 'processo'."

            # Lista para acumular erros
            errors = []
            inseridos_com_sucesso = 0

            # Inicia uma sessão com o banco de dados
            with self.repository.get_session() as session:
                try:
                    for _, row in df_turmas.iterrows():
                        # Verifica se o ID já existe no banco
                        turma_existente = session.query(Turma).filter_by(id=int(row['id'])).first()
                        if turma_existente:
                            errors.append(f"Erro: o ID {row['id']} já existe no banco de dados.")
                            continue

                        # Cria uma nova instância de Turma
                        nova_turma = Turma(
                            id=int(row['id']),
                            nome=row['nome'],
                            data=self.converter_data(row['data']),  # Converte a data para o formato correto
                            processo=int(row['processo'])
                        )

                        # Adiciona a nova turma à sessão
                        session.add(nova_turma)
                        inseridos_com_sucesso += 1

                    # Comita a transação para salvar no banco de dados
                    session.commit()

                    # Mensagem final com sucesso parcial ou total
                    if errors:
                        return False, (
                            f"Algumas turmas não foram inseridas devido a erros:\n"
                            f"{'\n'.join(errors)}\n"  # Usando \n para separar cada erro
                            f"Turmas inseridas com sucesso: {inseridos_com_sucesso}."
                        )
                    return True, f"Todas as turmas ({inseridos_com_sucesso}) foram inseridas com sucesso!"
                except Exception as e:
                    session.rollback()  # Reverte as alterações em caso de erro
                    return False, f"Erro ao inserir turmas no banco de dados: {str(e)}"
        except Exception as e:
            return False, f"Erro ao processar o arquivo Excel: {str(e)}"

    def select(self):
        """Retorna todas as turmas do banco de dados."""
        with self.repository.get_session() as session:
            try:
                turmas = session.query(Turma).all()
                return turmas  # Retorna a lista de turmas
            except Exception as e:
                print(f"Erro ao obter turmas: {e}")
                return []

    def _ver_informacoes_turmas(self, session):
        try:
            turmas = session.query(Turma).all()
            if turmas:
                data = [{
                    'ID': turma.id,
                    'Nome': turma.nome,
                    'Data': turma.data,
                    'Processo': turma.processo
                } for turma in turmas]

                df = pd.DataFrame(data)
                print("Turmas encontradas:")
                print(df)
            else:
                print('Nenhuma turma encontrada.')
        except Exception as e:
            print(f"Erro ao obter turmas: {e}")

    def _ver_alunos_turma(self, turma_id):
        with self.repository.get_session() as session:
            try:
                turma = session.query(Turma).filter_by(id=turma_id).first()
                if turma and turma.aspirantes:
                    return turma.aspirantes  # Retorna os objetos diretamente
                else:
                    return []
            except Exception as e:
                print(f"Erro ao obter aspirantes: {e}")
                return []

    def update(self):
        with self.repository.get_session() as session:
            try:
                turma_nome = input('Digite o nome da turma: ').title()
                turma = session.query(Turma).filter_by(nome=turma_nome).first()

                if turma:
                    coluna_nome = input("Digite o nome da coluna que deseja modificar: ").strip().lower()

                    # Verifica se a coluna existe no modelo
                    if not hasattr(turma, coluna_nome):
                        raise Exception(f"A coluna '{coluna_nome}' não existe na tabela.")
                    
                    novo_valor = input(f"Digite o novo valor para a coluna '{coluna_nome}': ")
                    coluna_atributo = getattr(Turma, coluna_nome)  # Pegando a definição da coluna

                    if isinstance(coluna_atributo.type, Date):
                        try:
                            # Convertendo a string para um objeto datetime.date
                            novo_valor = datetime.strptime(novo_valor, '%d/%m/%Y').date()
                        except ValueError:
                            raise ValueError("Formato de data inválido. Use o formato 'DD/MM/YYYY'.")
                    elif isinstance(coluna_atributo.type, Integer):
                        try:
                            novo_valor = int(novo_valor)
                        except ValueError:
                            raise ValueError("O valor fornecido não é um número inteiro válido.")
                    elif isinstance(coluna_atributo.type, String):
                        novo_valor = str(novo_valor)
                    
                    # Atualiza a coluna com o novo valor
                    setattr(turma, coluna_nome, novo_valor)

                    session.commit()
                    print(f"Turma '{turma_nome}' atualizada com sucesso.")
                else:
                    print(f"Turma '{turma_nome}' não encontrada.")
            
            except ValueError as ve:
                print(f"Erro: {ve}")
            except Exception as e:
                session.rollback()
                print(f"Erro ao atualizar turma: {e}")

    def delete(self):
        with self.repository.get_session() as session:
            try:
                turma_nome = input('Digite o nome da turma que deseja remover: ').title()
                turma = session.query(Turma).filter_by(nome=turma_nome).first()

                if turma:
                    confirmacao = input(f"Tem certeza que deseja remover a turma '{turma.nome}'? (S/N): ").strip().lower()
                    if confirmacao == 's':
                        session.delete(turma)
                        session.commit()
                        print(f"Turma '{turma.nome}' removido com sucesso.")
                    else:
                        print(f"Remoção do turma '{turma.nome}' cancelada.")
                else:
                    print(f"Turma com nome '{turma_nome}' não encontrado.")
            except Exception as e:
                session.rollback()
                print(f"Erro ao remover turma: {e}")

    def converter_data(self, data):
        # Verifica se o valor de data é um Timestamp do Pandas
        if isinstance(data, pd.Timestamp):
            return data.date()  # Retorna a data como um objeto date do Python
        # Caso contrário, tenta converter a string para um objeto date
        return datetime.strptime(data, '%d/%m/%Y').date()
    
    # Função para retornar o total de professores
    def count_turmas(self):
        with self.repository.get_session() as session:
            try:
                total = session.query(Turma).count()
                return total
            except Exception as e:
                print(f"Erro ao contar turmas: {e}")
                return None
            
    def get_by_id(self, turma_id):
        """Busca uma turma pelo ID."""
        with self.repository.get_session() as session:
            return session.query(Turma).filter_by(id=turma_id).first()
        
    def get_last_id(self):
        with self.repository.get_session() as session:
            return session.query(func.max(Turma.id)).scalar()
        
    def get_by_slug(self, slug):
        """Busca a turma pelo slug gerado."""
        turmas = self.select()  # Retorna todas as turmas cadastradas
        for turma in turmas:
            if turma_slug(turma.id) == slug:
                return turma
        return None

    def gerar_turma_aspirantes_graph(self):
        """
        Conta o número de aspirantes em cada turma e gera um gráfico de barras horizontais com uma cor verde específica.
        Retorna os dados do gráfico no formato JSON.
        """
        with self.repository.get_session() as session:
            try:
                turmas = (
                    session.query(Turma)
                    .options(joinedload(Turma.aspirantes))
                    .all()
                )

                # Extraindo os dados diretamente
                nomes_turmas = [turma.nome for turma in turmas]
                num_aspirantes = [len(turma.aspirantes) for turma in turmas]

                # Ordena os dados em ordem decrescente pelo número de aspirantes
                dados_ordenados = sorted(
                    zip(nomes_turmas, num_aspirantes),
                    key=lambda x: x[1],
                    reverse=True
                )
                nomes_turmas, num_aspirantes = zip(*dados_ordenados)

                # Cor única verde (cor definida pelo código '#008965')
                cor_unica = "#008965"

                # Cria as barras horizontais com a cor única
                bars = Bar(
                    x=num_aspirantes,  # Número de aspirantes no eixo X
                    y=nomes_turmas,    # Turmas no eixo Y
                    orientation="h",   # Barras horizontais
                    marker=dict(color=cor_unica)  # Cor única verde
                )

                # Define o layout do gráfico
                layout = Layout(
                    title="Número de Aspirantes por Turma",
                    xaxis=dict(title="Número de Aspirantes"),
                    yaxis=dict(title="Turma", automargin=True),
                    font=dict(size=14),
                    showlegend=False
                )

                # Cria o gráfico com os dados e layout
                fig = Figure(data=[bars], layout=layout)

                # Retorna o gráfico no formato JSON
                return fig.to_json()

            except Exception as e:
                return None, json.dumps(f"Erro ao gerar gráfico de aspirantes por turma: {e}")

