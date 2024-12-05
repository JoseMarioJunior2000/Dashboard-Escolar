from models.configs.connection import DataBaseConnection
from sqlalchemy import Integer, String, Boolean, func
from models.entities.aspirante import Aspirante
from sqlalchemy.exc import IntegrityError
from models.entities.turma import Turma
from flask import jsonify
import pandas as pd
import plotly.graph_objs as go
import plotly.io as pio
from sqlalchemy import func, case
import base64

class AspiranteRepository:
    def __init__(self, repository: DataBaseConnection):
        self.repository = repository

    def select(self, nome=None, email=None, idade=None):
        with self.repository.get_session() as session:
            query = session.query(Aspirante)
            
            if nome:
                # Filtrar pelo nome completo ou por nomes que começam com o valor dado
                query = query.filter(Aspirante.nome.ilike(f'{nome}%'))  # '%' após o nome para permitir qualquer coisa depois
            if email:
                query = query.filter(Aspirante.email.ilike(f'%{email}%'))
            if idade is not None:  # Verifica se a idade não é None
                query = query.filter(Aspirante.idade == idade)

            # Retorna o primeiro resultado que atende aos critérios, ou None se não houver
            return query.first()
    
    def add(self, id, nome, email, idade, sexo, uf, fone, ativo, turma_id=None, foto=None, aspirantld=None):
        with self.repository.get_session() as session:
            try:
                # Criação do novo aspirante
                novo_aspirante = Aspirante(
                    id=id,
                    nome=nome,
                    email=email,
                    idade=idade,
                    sexo=sexo,
                    uf=uf,
                    fone=fone,
                    ativo=ativo.lower() == 's',  # Supondo que 'ativo' é 'S' ou 'N'
                    aspirantld=aspirantld,  # Isso pode ser None se não fornecido
                    foto=foto  # Isso também pode ser None se não fornecido
                )

                # Se o ID da turma foi fornecido, faz a associação
                if turma_id:
                    turma = session.query(Turma).filter_by(id=turma_id).first()
                    if turma:
                        novo_aspirante.turmas.append(turma)

                    else:
                        return False, f"Erro: Turma com ID {turma_id} não encontrada."

                session.add(novo_aspirante)
                session.commit()
                return True, "Aspirante adicionado com sucesso."

            except Exception as e:
                session.rollback()
                return False, f"Erro ao adicionar aspirante: {e}"

    def insert_excel(self, caminho_arquivo):
        try:
            excel_data = pd.ExcelFile(caminho_arquivo)
            if 'aspirantes' not in excel_data.sheet_names or 'turma_aspirantes' not in excel_data.sheet_names:
                return False, "Erro: o arquivo não contém as abas obrigatórias 'aspirantes' e/ou 'turma_aspirantes'."

            df_aspirantes = pd.read_excel(caminho_arquivo, sheet_name='aspirantes')
            df_turma_aspirantes = pd.read_excel(caminho_arquivo, sheet_name='turma_aspirantes')

            aspirantes_cols = {'id', 'nome', 'sexo', 'uf', 'email', 'fone', 'idade', 'ativo', 'aspirantId', 'atualizado'}
            turma_aspirantes_cols = {'id_aspirante', 'id_turma'}

            if not aspirantes_cols.issubset(df_aspirantes.columns) or not turma_aspirantes_cols.issubset(df_turma_aspirantes.columns):
                return False, "Erro: verifique as colunas obrigatórias."

            errors = []
            with self.repository.get_session() as session:
                existing_ids = {int(id_[0]) for id_ in session.query(Aspirante.id).all()}
                aspirantes_dict = {}

                for _, row in df_aspirantes.iterrows():
                    novo_id = int(row['id'])
                    
                    # Verificar duplicação antes da inserção
                    if novo_id in existing_ids:
                        error_message = f"Erro: ID {novo_id} já existe no banco de dados."
                        errors.append(error_message)
                        print(error_message)
                        # Rollback e retorno com erro de ID duplicado
                        session.rollback()
                        return False, f"{error_message}. Nenhum dado foi inserido."

                    ativo = True if str(row['ativo']).strip().lower() == 'sim' else False
                    novo_aspirante = Aspirante(
                        id=novo_id,
                        nome=row['nome'],
                        sexo=row['sexo'],
                        uf=row['uf'],
                        email=row['email'],
                        fone=row['fone'],
                        idade=int(row['idade']),
                        ativo=ativo,
                        aspirantld=int(row['aspirantId']),
                        foto=None
                    )
                    session.add(novo_aspirante)
                    aspirantes_dict[novo_id] = novo_aspirante

                session.flush()

                for _, row in df_turma_aspirantes.iterrows():
                    aspirante_id = int(row['id_aspirante'])
                    turma_id = int(row['id_turma'])

                    if aspirante_id in aspirantes_dict:
                        aspirante = aspirantes_dict[aspirante_id]
                        turma = session.query(Turma).filter_by(id=turma_id).first()
                        if turma:
                            aspirante.turmas.append(turma)
                        else:
                            error_message = f"Turma com ID {turma_id} não encontrada para o aspirante ID {aspirante_id}."
                            errors.append(error_message)
                            print(error_message)
                    else:
                        error_message = f"Aspirante com ID {aspirante_id} não encontrado para associação com a turma."
                        errors.append(error_message)
                        print(error_message)

                session.commit()

                if errors:
                    return True, f"Alguns aspirantes foram inseridos com sucesso, mas ocorreram erros: {errors}"
                return True, "Todos os aspirantes e associações com turmas foram inseridos com sucesso!"

        except Exception as e:
            # Realizar o rollback em caso de erro inesperado
            session.rollback()
            return False, f"Erro ao processar o arquivo: {str(e)}"

    def update(self, id, coluna, valor):
        with self.repository.get_session() as session:
            try:
                aspirante = session.query(Aspirante).get(id)
                if not aspirante:
                    raise ValueError("Aspirante não encontrado")
                
                # Atualiza a coluna específica com o novo valor
                setattr(aspirante, coluna, valor)
                
                session.commit()  # Confirma as alterações no banco de dados
                return True, 'Alterações realizadas com sucesso!'
            except Exception as e:
                # Desfaz as alterações em caso de erro
                session.rollback()  
                return False, f'Não foi possível alterar os campos: {e}'


    def delete(self, id):
        with self.repository.get_session() as session:
            aspirante = session.query(Aspirante).get(id)
            if aspirante:
                session.delete(aspirante)
                session.commit()
            else:
                raise ValueError("Aspirante não encontrado.")

    # Função para retornar o total de aspirantes
    def count_aspirantes(self):
        with self.repository.get_session() as session:
            try:
                total = session.query(Aspirante).count()
                return total
            except Exception as e:
                print(f"Erro ao contar aspirantes: {e}")
                return None
            
    def get_all(self):
        try:
            with self.repository.get_session() as session:
                # Obtém todos os registros de aspirantes
                return session.query(Aspirante).all()
        except Exception as e:
            print(f"Erro ao obter todos os aspirantes: {e}")
            return None  # Ou trate conforme necessário
        
    def get_last_id(self):
        with self.repository.get_session() as session:
            return session.query(func.max(Aspirante.id)).scalar()
        
    def get_by_id(self, id):
        with self.repository.get_session() as session:
            return session.query(Aspirante).filter_by(id=id).first()
        
    def get_aspirante_com_foto_base64(self, id):
        with self.repository.get_session() as session:
            aspirante = session.query(Aspirante).get(id)
            if aspirante and aspirante.foto:
                aspirante.foto_base64 = base64.b64encode(aspirante.foto).decode('utf-8')
            return aspirante
    
    def grafico_genero(self):
        with self.repository.get_session() as session:
            # Consulta para contar a quantidade de aspirantes masculinos e femininos
            contagem_sexo = session.query(Aspirante.sexo, func.count(Aspirante.id)).group_by(Aspirante.sexo).all()
            
            # Organizando os dados para o gráfico
            sexos = ['Masculino', 'Feminino']
            quantidades = [0, 0]  # Inicializa com 0 para masculino e feminino
            
            # Preenchendo as quantidades de acordo com a contagem dos dados
            for sexo, quantidade in contagem_sexo:
                if sexo == 'M':
                    quantidades[0] = quantidade
                elif sexo == 'F':
                    quantidades[1] = quantidade

            # Definindo a paleta de cores em tons de verde
            cores_verde = ['#008965', '#00af80']  # Verde escuro e verde claro
            
            # Criando o gráfico de pizza
            fig = go.Figure(
                data=[go.Pie(labels=sexos, values=quantidades, hole=0.3, marker=dict(colors=cores_verde))],  # Gráfico de pizza com um buraco no meio e cores personalizadas
                layout=go.Layout(
                    title="Aspirantes por Sexo",
                    autosize=True,  # Torna o gráfico ajustável
                    margin=dict(t=30, l=20, r=20, b=20)  # Ajusta margens conforme necessário
                )
            )
            
            # Convertendo o gráfico para JSON
            return pio.to_json(fig)
        
    def criar_grafico_faixas_etarias(self):
        with self.repository.get_session() as session:
            # Criando uma consulta para categorizar idades em faixas
            faixas_etarias = case(
                (Aspirante.idade.cast(Integer) <= 18, "Até 18 anos"),
                ((Aspirante.idade.cast(Integer) >= 19) & (Aspirante.idade.cast(Integer) <= 30), "19 até 30 anos"),
                ((Aspirante.idade.cast(Integer) >= 31) & (Aspirante.idade.cast(Integer) <= 45), "31 até 45 anos"),
                ((Aspirante.idade.cast(Integer) >= 46) & (Aspirante.idade.cast(Integer) <= 60), "46 até 60 anos"),
                else_="Idade não informada"
            )

            # Consulta para contar aspirantes por faixa etária
            contagem_faixas = (
                session.query(faixas_etarias.label("faixa_etaria"), func.count(Aspirante.id))
                .group_by("faixa_etaria")
                .all()
            )
            
            # Organizando os dados para o gráfico
            faixas = [
                "Até 18 anos",
                "19 até 30 anos",
                "31 até 45 anos",
                "46 até 60 anos",
                "Idade não informada",
            ]
            quantidades = [0] * len(faixas)  # Inicializa todas as faixas com 0

            # Preenchendo os dados da consulta
            faixa_indices = {faixa: i for i, faixa in enumerate(faixas)}
            for faixa, quantidade in contagem_faixas:
                if faixa in faixa_indices:
                    quantidades[faixa_indices[faixa]] = quantidade
            
            # Criando o gráfico de barras
            fig = go.Figure(
                data=[
                    go.Bar(x=faixas, y=quantidades, marker=dict(color='#008965'))  # Barra com cor verde
                ],
                layout=go.Layout(
                    title="Aspirantes por Idade",
                    xaxis=dict(title="Faixa Etária"),
                    yaxis=dict(title="Quantidade"),
                    autosize=True,  # Torna o gráfico ajustável
                    margin=dict(t=30, l=20, r=20, b=20)  # Ajusta margens conforme necessário
                )
            )
            
            # Convertendo o gráfico para JSON
            return pio.to_json(fig)