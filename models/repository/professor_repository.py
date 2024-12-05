from models.configs.connection import DataBaseConnection
from models.entities.professor import Professor
from sqlalchemy import Integer, String
import pandas as pd
import os
from flask import jsonify

class ProfessorRepository:
    def __init__(self, repository: DataBaseConnection):
        self.repository = repository

    def select(self):
        filtros = self.filtros()
        nome, trilha = filtros
        id_professor = self.buscar_professores_com_filtros(nome, trilha)

    def filtros(self):
        try:
            nome = input('Digite o nome do professor: ').title()
            trilha = input('Digite a trilha do professor: ')

            return nome, trilha
        except Exception as e:
            print(f'Erro ao aplicar filtros: {e}')


    def buscar_professores_com_filtros(self, nome=None, trilha=None):
        with self.repository.get_session() as session:
            try:
                # Consulta base
                query = session.query(Professor)

                # Aplicação dos filtros conforme o usuário escolher
                if nome:
                    query = query.filter(Professor.nome == nome)
                if trilha:
                    query = query.filter(Professor.trilha == trilha)

                # Busca os encontros filtrados
                professores_filtrados = query.all() 

                # Verificar se há resultados
                if professores_filtrados:
                    df = pd.DataFrame([{
                        'ID': professor.id,
                        'Nome': professor.nome,
                        'Trilha': professor.trilha
                    } for professor in professores_filtrados])

                    print("\nProfessores encontrados:")
                    print(df)
                else:
                    print("Professor não encontrado.")
            except Exception as e:
                print(f"Erro ao buscar Professor: {e}")

    def insert(self):
        escolha = input("Deseja inserir o novo professor manualmente (1) ou por um arquivo Excel (2)? ").strip()

        if escolha == '1':
            self.insert_manual()
        elif escolha == '2':
            self.insert_excel()
        else:
            print("Opção inválida. Tente novamente.")
            return
        
    def insert_manual(self):
        try:
            # Coleta os dados manualmente
            id = int(input('Digite o id do professor: '))
            nome = input("Digite o nome do professor: ")
            trilha = input("Digite o nome da trilha do professor: ")

            with self.repository.get_session() as session:
                novo_professor = Professor(
                    id=id,
                    nome=nome,
                    trilha=trilha
                )
                    
                session.add(novo_professor)
                session.commit()
                print("Professor cadastrado com sucesso!")
                print(novo_professor.__repr__())
                return novo_professor
        except Exception as e:
            session.rollback()
            print(f"Erro ao inserir professor: {e}")
            return None
        
    def insert_excel(self):
        try:
            # Definindo o caminho relativo para o arquivo Excel
            caminho_arquivo = os.path.join(os.path.dirname(__file__), '..', '..', 'BD-EdTech-2024-09-30 a 2024-10-04 sem formulas.xlsm')
            caminho_arquivo = os.path.normpath(caminho_arquivo)

            print(f"Caminho relativo para o arquivo: {caminho_arquivo}")

            df_professores = pd.read_excel(caminho_arquivo, sheet_name='professores')

            with self.repository.get_session() as session:
                for _, row in df_professores.iterrows():
                    novo_professor = Professor(
                        id=int(row['id']),
                        nome=row['nome'],
                        trilha=row['trilha']
                    )

                    session.add(novo_professor)

                session.commit()
                print("Todos os professores foram inseridos com sucesso!")
        
        except Exception as e:
            session.rollback()
            print(f"Erro ao inserir os professores a partir do arquivo Excel: {e}")

            
    def update(self):
        with self.repository.get_session() as session:
            try:
                professor_nome = input('Digite o nome do professor: ').title()
                professor = session.query(Professor).filter_by(nome=professor_nome).first()

                if professor:
                    coluna_nome = input("Digite o nome da coluna que deseja modificar: ").strip().lower()
                    if not hasattr(professor, coluna_nome):
                        raise Exception(f"A coluna '{coluna_nome}' não existe na tabela.")
                    
                    novo_valor = input(f"Digite o novo valor para a coluna '{coluna_nome}': ")
                    coluna_atributo = getattr(Professor, coluna_nome)  # Pegando a definição da coluna

                    if isinstance(coluna_atributo.type, String):
                        try:
                            novo_valor = str(novo_valor.title())
                        except ValueError as e:
                            raise print(f'Não foi possível atualizar a coluna {coluna_nome}: {e}')
                        
                    if isinstance(coluna_atributo.type, Integer):
                        # Normaliza o input para um valor inteiro
                        try:
                            novo_valor = int(novo_valor)
                        except ValueError:
                            raise ValueError("O valor fornecido não é um número inteiro válido.")

                    setattr(professor, coluna_nome, novo_valor)

                    session.commit()
                    print(f"Professor '{professor_nome}' atualizado com sucesso.")
                    print(professor.__repr__())
                else:
                    print(f"Professor '{professor_nome}' não encontrado.")
            except ValueError:
                print("Erro: Valor inválido fornecido. Certifique-se de que o novo valor corresponde ao tipo de dados esperado.")
            except Exception as e:
                session.rollback()
                print(f"Erro ao atualizar aluno: {e}")

    def delete(self):
        with self.repository.get_session() as session:
            try:
                professor_nome = input('Digite o nome do professor que deseja remover: ').title()
                professor = session.query(Professor).filter_by(nome=professor_nome).first()

                if professor:
                    confirmacao = input(f"Tem certeza que deseja remover o aspirante '{professor.nome}'? (S/N): ").strip().lower()
                    if confirmacao == 's':
                        session.delete(professor)
                        session.commit()
                        print(f"Professor '{professor.nome}' removido com sucesso.")
                    else:
                        print(f"Remoção do professor '{professor.nome}' cancelada.")
                else:
                    print(f"Professor com nome '{professor_nome}' não encontrado.")
            except Exception as e:
                session.rollback()
                print(f"Erro ao remover professor: {e}")

    def count_professores(self):
        """
        Recupera todos os professores inseridos no banco de dados com exceção daqueles asociados à trilha Momento Empresa 
        e retorna um número inteiro mostrando o total de professores no Alpha EdTech.
        """
        with self.repository.get_session() as session:
            try:
                # Filtrar professores com trilha diferente de "ME"
                total = session.query(Professor).filter(Professor.trilha != "ME").count()
                return total
            except Exception as e:
                return None, jsonify(f"Erro ao contar professores: {e}")
            
    def listar_todos(self):
        with self.repository.get_session() as session:
            return session.query(Professor.id, Professor.nome).all()