from models.configs.connection import DataBaseConnection
from models.entities.atividade import Atividade
from models.entities.aspirante import Aspirante
from models.entities.professor import Professor
from models.entities.encontro import Encontro
from sqlalchemy import Integer, Boolean, Text
from datetime import datetime
import pandas as pd
import os

class AtividadeRepository:
    def __init__(self, repository: DataBaseConnection):
        self.repository = repository

    def select(self):
        filtros = self.filtros()
        trilha, data, hora, modulo, assunto, nome_professor = filtros
        id_encontro = self.buscar_encontros_com_filtros(trilha, data, hora, modulo, assunto, nome_professor)
        self.select_entregas(id_encontro)

    def filtros(self):
        try:
            trilha = input('Digite o nome da trilha (ou deixe em branco): ').title()
            
            # Data no formato DD/MM/AAAA, com conversão para o formato apropriado
            data_input = input("Digite a data no formato DD/MM/AAAA (ou deixe em branco): ")
            data = None
            if data_input:
                try:
                    data = datetime.strptime(data_input, "%d/%m/%Y").date()  # Converter para o formato date
                except ValueError:
                    print("Formato de data inválido. Use DD/MM/AAAA.")
            
            # Hora no formato HH:MM, com conversão para o formato de hora do banco
            hora_input = input("Digite o horário no formato HH:MM (ou deixe em branco): ")
            hora = None
            if hora_input:
                try:
                    hora = datetime.strptime(hora_input, "%H:%M").time()  # Converter para o formato time
                except ValueError:
                    print("Formato de hora inválido. Use HH:MM.")
            
            modulo = input('Digite o nome do módulo (ou deixe em branco): ')
            assunto = input('Digite o nome do assunto (ou deixe em branco): ')
            nome_professor = input('Digite o nome do professor (ou deixe em branco): ').title()

            return trilha, data, hora, modulo, assunto, nome_professor
        except Exception as e:
            print(f'Erro ao aplicar filtros: {e}')
            return None, None, None, None, None, None

    # Função para aplicar filtros e retornar os encontros em um DataFrame
    def buscar_encontros_com_filtros(self, trilha=None, data=None, hora=None, modulo=None, assunto=None, nome_professor=None):
        with self.repository.get_session() as session:
            try:
                # Consulta base
                query = session.query(Encontro).join(Professor)

                # Aplicação dos filtros conforme o usuário escolher
                if trilha:
                    query = query.filter(Encontro.trilha == trilha)
                if data:
                    query = query.filter(Encontro.data == data)
                if hora:
                    query = query.filter(Encontro.hora == hora)
                if modulo:
                    query = query.filter(Encontro.modulo == modulo)
                if assunto:
                    query = query.filter(Encontro.assunto == assunto)
                if nome_professor:
                    query = query.filter(Professor.nome == nome_professor)

                # Busca os encontros filtrados
                encontros_filtrados = query.all()

                # Verificar se há resultados
                if encontros_filtrados:
                    # Criando um DataFrame para exibir os encontros filtrados
                    df = pd.DataFrame([{
                        'ID': encontro.id,
                        'Trilha': encontro.trilha,
                        'Data': encontro.data,
                        'Hora': encontro.hora,
                        'Módulo': encontro.modulo,
                        'Assunto': encontro.assunto,
                        'Duração': encontro.duracao,
                        'Professor ID': encontro.id_professor
                    } for encontro in encontros_filtrados])

                    print("\nEncontros filtrados:")
                    print(df)

                    # Pergunta ao usuário qual ID de encontro deseja selecionar
                    escolha = int(input("\nDigite o ID do encontro que deseja visualizar: "))

                    # Procurar o encontro selecionado
                    encontro_selecionado = next((encontro for encontro in encontros_filtrados if encontro.id == escolha), None)

                    if encontro_selecionado:
                        print(f"\nEncontro selecionado: ID {encontro_selecionado.id}")
                        return encontro_selecionado.id
                    else:
                        print("ID de encontro inválido.")
                        return None
                else:
                    print("Nenhum encontro encontrado com esses filtros.")
                    return None
            except Exception as e:
                print(f"Erro ao buscar encontros: {e}")
                return None

    # Função para buscar entregas com base no id_encontro
    def select_entregas(self, id_encontro):
        with self.repository.get_session() as session:
            try:
                # Busca as atividades associadas ao encontro específico
                query = session.query(Atividade).filter(Atividade.id_encontro == id_encontro)
                atividades = query.all()

                # Coleta as informações em uma lista
                entregas_data = []
                for atividade in atividades:
                    aspirante = session.query(Aspirante).filter(Aspirante.id == atividade.id_aspirante).first()
                    entregas_data.append({
                        'Aspirante': aspirante.nome,
                        'Entrega': 'Sim' if atividade.entrega else 'Não',
                        'Dias de Atraso': atividade.atraso if atividade.entrega else 'N/A',
                        'Notas': atividade.notas if atividade.notas is not None else 'Sem nota'
                    })

                # Cria um DataFrame a partir da lista
                df_entregas = pd.DataFrame(entregas_data)

                print(df_entregas)

                return df_entregas  # Retorna o DataFrame

            except Exception as e:
                print(f"Erro ao buscar entregas de atividades: {e}")
                return pd.DataFrame()  # Retorna um DataFrame vazio em caso de erro
            
    def insert(self):
        escolha = input("Deseja inserir a nova atividade manualmente (1) ou por um arquivo Excel (2)? ").strip()

        if escolha == '1':
            self.insert_manual()
        elif escolha == '2':
            self.insert_excel()
        else:
            print("Opção inválida. Tente novamente.")
            return
    
    # Método para inserir manualmente uma nova Atividade
    def insert_manual(self):
        with self.repository.get_session() as session:
            try:
                # Solicitar os inputs do usuário
                id = int(input('Digite o ID da atividade: '))
                id_encontro = int(input("Digite o ID do encontro: "))
                id_aspirante = int(input("Digite o ID do aspirante: "))
                entrega = input("A atividade foi entregue? (S/N): ").strip().lower() == 's'
                atraso = int(input("Quantos dias de atraso (se entregue): ") or 0) if entrega else 0
                notas = input("Digite a nota (ou deixe em branco se não houver): ")
                notas = int(notas) if notas and notas.strip() else None  # Verifica se notas não é vazio e não é só espaço

                # Criar uma nova instância de Atividade
                nova_atividade = Atividade(
                    id=id,
                    id_encontro=id_encontro,
                    id_aspirante=id_aspirante,
                    entrega=entrega,
                    atraso=atraso,
                    notas=notas
                )

                # Adicionar a nova atividade à sessão
                session.add(nova_atividade)
                # Commitar a transação para salvar no banco
                session.commit()
                print(f"Atividade adicionada com sucesso!")
                print(nova_atividade.__repr__())
                return nova_atividade

            except Exception as e:
                session.rollback()
                print(f"Erro ao inserir a atividade: {e}")
                return None
            
    def insert_excel(self):
        try:
            caminho_arquivo = os.path.join(os.path.dirname(__file__), '..', '..', 'BD-EdTech-2024-09-30 a 2024-10-04 sem formulas.xlsm')
            caminho_arquivo = os.path.normpath(caminho_arquivo)

            print(f"Caminho relativo para o arquivo: {caminho_arquivo}")

            # Lendo o Excel, planilha 'atividades'
            df_atividades = pd.read_excel(caminho_arquivo, sheet_name='atividades')

            with self.repository.get_session() as session:
                try:
                    for _, row in df_atividades.iterrows():
                        # Verifica se a entrega foi feita
                        entrega = True if row['entrega'] == 1 else False
                        
                        # Verifica se a nota está vazia ou não
                        if pd.isna(row['nota']) or row['nota'] == '' or row['nota'] == ' ':
                            notas = None
                        else:
                            notas = int(row['nota']) if pd.notna(row['nota']) else None  # Verifica se não é NaN

                        atraso = int(row['atraso']) if not pd.isna(row['atraso']) else None

                        # Cria uma nova instância de Atividade
                        nova_atividade = Atividade(
                            id=int(row['id']),
                            id_encontro=int(row['id_encontro']),
                            id_aspirante=int(row['id_aspirante']),
                            entrega=entrega,
                            atraso=atraso,
                            notas=notas
                        )

                        # Adiciona a nova atividade à sessão
                        session.add(nova_atividade)

                    # Comita a transação para salvar no banco de dados
                    session.commit()
                    print("Todas as atividades foram inseridas com sucesso!")
                except Exception as e:
                    session.rollback()
                    print(f"Erro ao inserir as atividades a partir do Excel: {e}")

        except Exception as e:
            print(f"Erro ao ler o arquivo Excel: {e}")

    def update(self):
        with self.repository.get_session() as session:
            try:
                atividade_id = int(input('Digite o ID da atividade: '))
                atividade = session.query(Atividade).filter_by(id=atividade_id).first()

                if atividade:
                    coluna_nome = input("Digite o nome da coluna que deseja modificar: ").strip().lower()
                    if not hasattr(atividade, coluna_nome):
                        raise Exception(f"A coluna '{coluna_nome}' não existe na tabela.")
                    
                    novo_valor = input(f"Digite o novo valor para a coluna '{coluna_nome}': ")
                    coluna_atributo = getattr(Atividade, coluna_nome)  # Pegando a definição da coluna

                    if isinstance(coluna_atributo.type, Integer):
                        # Normaliza o input para um valor inteiro
                        try:
                            novo_valor = int(novo_valor)
                        except ValueError:
                            raise ValueError("O valor fornecido não é um número inteiro válido.")
                        
                    elif isinstance(coluna_atributo.type, Boolean):
                        # Normaliza o input para um valor booleano
                        novo_valor = novo_valor.lower() in ['true', '1', 't', 'y', 'yes']

                    setattr(atividade, coluna_nome, novo_valor)

                    session.commit()
                    print(f"Atividade '{atividade_id}' atualizado com sucesso.")
                else:
                    print(f"Aluno '{atividade_id}' não encontrado.")
            except ValueError:
                print("Erro: Valor inválido fornecido. Certifique-se de que o novo valor corresponde ao tipo de dados esperado.")
            except Exception as e:
                session.rollback()
                print(f"Erro ao atualizar aluno: {e}")
    
    def delete(self):
        with self.repository.get_session() as session:
            try:
                id_atividade = int(input("Digite o ID da atividade que deseja deletar: "))
                
                # Busca a atividade pelo ID
                atividade = session.query(Atividade).filter(Atividade.id == id_atividade).first()

                if atividade:
                    confirmacao = input(f"Tem certeza que deseja remover a atividade'? (S/N): ").strip().lower()
                    if confirmacao == 's':
                        session.delete(atividade)
                        session.commit()
                        print(f"Atividade ID {id_atividade} deletada com sucesso!")
                    else:
                        print(f"Remoção da atividade cancelada.")
                else:
                    print("Atividade não encontrada.")
                    
            except Exception as e:
                session.rollback()
                print(f"Erro ao deletar a atividade: {e}")