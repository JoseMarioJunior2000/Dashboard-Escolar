from models.configs.connection import DataBaseConnection
from models.entities.encontro import Encontro, encontro_aspirantes
from models.entities.atividade import Atividade
import pandas as pd
import os
from sqlalchemy import insert, delete, update
from datetime import datetime, time

class UpdateRepository:
    def __init__(self, repository: DataBaseConnection):
        self.repository = repository

    def update(self):
        try:
            with self.repository.get_session() as session:
                # Definindo o caminho relativo para o arquivo Excel
                #caminho_arquivo = os.path.join(os.path.dirname(__file__), '..', '..', 'BD-EdTech-2024-09-16_a_20_atualização.xlsm')
                #caminho_arquivo = os.path.join(os.path.dirname(__file__), '..', '..', 'BD-EdTech-2024-09-23_a_27_atualização.xlsm')
                #caminho_arquivo = os.path.join(os.path.dirname(__file__), '..', '..', 'BD-EdTech-2024-09-30_a_10_04_atualização.xlsm')
                #caminho_arquivo = os.path.join(os.path.dirname(__file__), '..', '..', 'BD-EdTech-2024-09-30 a 2024-10-04 sem formulas.xlsm')
                caminho_arquivo = os.path.join(os.path.dirname(__file__), '..', '..', 'BD-EdTech-2024-10-06_a_10_13_atualização.xlsm')
                caminho_arquivo = os.path.normpath(caminho_arquivo)

                print(f"Caminho relativo para o arquivo: {caminho_arquivo}")
                # Chama a função para processar os encontros
                self.excel_encontro(session, caminho_arquivo)

                # Chama a função para processar as atividades
                self.excel_atividade(session, caminho_arquivo)

                # Commita todas as operações de uma só vez, garantindo integridade
                session.commit()
                print("Atualização bem-sucedida, todas as operações foram commitadas.")

        except Exception as e:
            session.rollback()  # Faz rollback de todas as operações se houver erro
            print(f"Erro ao realizar atualização: {e}")

    def excel_encontro(self, session, caminho_arquivo):
        try:
            df_encontros = pd.read_excel(caminho_arquivo, sheet_name='encontros')
            df_encontro_aspirantes = pd.read_excel(caminho_arquivo, sheet_name='encontro_aspirantes')

            # Primeiro insere todos os encontros
            for _, row in df_encontros.iterrows():
                atualizacao = int(row['atualizado'])
                
                if atualizacao == 1:
                    # Inserir nova atividade
                    self.insert_encontro(session, row)
                elif atualizacao == 2:
                    # Atualizar atividade existente
                    self.update_encontro(session, row)
                elif atualizacao == 3:
                    # Deletar atividade existente
                    self.delete_encontro(session, row)
                else:
                    # Inserir nova atividade
                    self.insert_encontro(session, row)

            # Faz um flush para garantir que todos os encontros foram "empurrados"
            session.flush()

            # Agora insere as associações
            self.insert_associacoes(session, df_encontro_aspirantes)

            print("Todos os encontros e suas associações foram inseridos com sucesso!")

        except Exception as e:
            print(f"Ocorreu um erro ao processar o Excel: {e}")
            raise
    
    def insert_encontro(self, session, row):
        """Insere um novo encontro no banco de dados."""
        atividade = True if row['atividade'] == 1 else False

        novo_encontro = Encontro(
            id=int(row['id']),
            trilha=row['trilha'],
            data=self.converter_data(row['data']),  # Converter para data
            hora=self.converter_hora(row['hora']),  # Converter para hora
            modulo=row['modulo'],
            assunto=row['assunto'] if not pd.isna(row['assunto']) else None,
            duracao=int(row['duracao']),
            id_professor=int(row['id_professor']),
            atividade=atividade,
            meetingId=int(row['meetingId']) if not pd.isna(row['meetingId']) else None
        )

        session.add(novo_encontro)
        print(f"Encontro {novo_encontro.id} inserido com sucesso.")

    def update_encontro(self, session, row):
        """Atualiza um encontro existente no banco de dados."""
        encontro_id = int(row['id'])

        stmt = (
            update(Encontro).
            where(Encontro.id == encontro_id).
            values(
                trilha=row['trilha'],
                data=self.converter_data(row['data']),
                hora=self.converter_hora(row['hora']),
                modulo=row['modulo'],
                assunto=row['assunto'] if not pd.isna(row['assunto']) else None,
                duracao=int(row['duracao']),
                id_professor=int(row['id_professor']),
                atividade=True if row['atividade'] == 1 else False,
                meetingId=int(row['meetingId']) if not pd.isna(row['meetingId']) else None
            )
        )

        session.execute(stmt)
        print(f"Encontro {encontro_id} atualizado com sucesso.")

    def delete_encontro(self, session, row):
        """Deleta um encontro existente no banco de dados."""
        encontro_id = int(row['id'])

        stmt = delete(Encontro).where(Encontro.id == encontro_id)
        session.execute(stmt)
        print(f"Encontro {encontro_id} deletado com sucesso.")

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
        print("Associações de aspirantes inseridas com sucesso.")
        
    def excel_atividade(self, session, caminho_arquivo):
        try:

            # Lendo o Excel, planilha 'atividades'
            df_atividades = pd.read_excel(caminho_arquivo, sheet_name='atividades')
            print(df_atividades.isnull().sum())

            for _, row in df_atividades.iterrows():
                atualizacao = int(row['atualizado'])
                if atualizacao == 1:
                    # Inserir nova atividade
                    self.insert_atividade(session, row)
                elif atualizacao == 2:
                    # Atualizar atividade existente
                    self.update_atividade(session, row)
                elif atualizacao == 3:
                    # Deletar atividade existente
                    self.delete_atividade(session, row)

                # Faz um flush para garantir que as operações foram "empurradas"
                session.flush()

        except Exception as e:
            print(f"Erro ao processar o arquivo Excel: {e}")
            raise
        
    def insert_atividade(self, session, row):
        try:
            entrega = True if row['entrega'] == 1 else False
            atraso = int(row['atraso']) if not pd.isna(row['atraso']) else None
            notas = int(row['nota']) if not pd.isna(row['nota']) else None
            
            nova_atividade = Atividade(
                id_encontro=int(row['id_encontro']),
                id_aspirante=int(row['id_aspirante']),
                entrega=entrega,
                atraso=atraso,
                notas=notas
            )
            
            session.add(nova_atividade)
            print(f"Atividade inserida!")

        except Exception as e:
            session.rollback()  # Reverte a transação em caso de erro
            print(f"Erro ao inserir atividade: {e}")

    def update_atividade(self, session, row):
        try:
            entrega = True if row['entrega'] == 1 else False
            notas = int(row['nota']) if not pd.isna(row['nota']) else None  # Certifique-se de que está verificando NaN
            atraso = int(row['atraso']) if not pd.isna(row['atraso']) else None

            atividade = session.query(Atividade).filter(
                Atividade.id == int(row['id']),
                Atividade.id_encontro == int(row['id_encontro']),
                Atividade.id_aspirante == int(row['id_aspirante'])
            ).first()
            
            if atividade:
                atividade.entrega = entrega
                atividade.atraso = atraso
                atividade.notas = notas
                print(f"Atividade atualizada: {atividade}!")
            else:
                print(f"Nenhuma atividade encontrada para atualizar com ID Encontro: {row['id_encontro']} e ID Aspirante: {row['id_aspirante']}")

        except Exception as e:
            session.rollback()  # Reverte a transação em caso de erro
            print(f"Erro ao atualizar atividade: {e}")

    def delete_atividade(self, session, row):
        try:
            atividade = session.query(Atividade).filter(
                Atividade.id_encontro == row['id_encontro'],
                Atividade.id_aspirante == row['id_aspirante']
            ).first()
            
            if atividade:
                session.delete(atividade)
                print(f"Atividade deletada: {atividade}")
            else:
                print(f"Nenhuma atividade encontrada para deletar com ID Encontro: {row['id_encontro']} e ID Aspirante: {row['id_aspirante']}")

        except Exception as e:
            session.rollback()  # Reverte a transação em caso de erro
            print(f"Erro ao deletar atividade: {e}")

    def converter_data(self, data):
        # Verifica se o valor de data é um Timestamp do Pandas
        if isinstance(data, pd.Timestamp):
            return data.date()  # Retorna a data como um objeto date do Python
        # Caso contrário, tenta converter a string para um objeto date
        return datetime.strptime(data, '%d/%m/%Y').date()

    def converter_hora(self, hora):
        if isinstance(hora, pd.Timestamp):
            return hora.time()  # Retorna o objeto time diretamente
        elif isinstance(hora, time):
            return hora  # Retorna diretamente se já for um objeto time
        elif isinstance(hora, str):
            return datetime.strptime(hora, '%H:%M').time()  # Converte para Time se for uma string
        else:
            print(f"Tipo inesperado para hora: {type(hora)}")  # Log de tipo inesperado
            return None  # Retorna None se o tipo não for esperado