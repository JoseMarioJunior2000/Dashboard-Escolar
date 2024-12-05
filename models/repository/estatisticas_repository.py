from models.configs.connection import DataBaseConnection
from models.entities.encontro import Encontro, encontro_aspirantes
from models.entities.aspirante import Aspirante
from models.entities.professor import Professor
import pandas as pd
from datetime import datetime

class EstatisticasRepository:
    def __init__(self, repository: DataBaseConnection):
        self.repository = repository

    def select(self):
        filtros = self.filtros()
        trilha, data, hora, modulo, assunto, nome_professor = filtros
        id_encontro = self.buscar_encontros_com_filtros(trilha, data, hora, modulo, assunto, nome_professor)
        self.calcular_presenca_encontro(id_encontro)

    def filtros(self):
        try:
            trilha = input('Digite o nome da trilha (ou deixe em branco): ')
            
            data_input = input("Digite a data no formato DD/MM/AAAA (ou deixe em branco): ")
            data = None
            if data_input:
                try:
                    data = datetime.strptime(data_input, "%d/%m/%Y").date()  
                except ValueError:
                    print("Formato de data inválido. Use DD/MM/AAAA.")
            
            hora_input = input("Digite o horário no formato HH:MM (ou deixe em branco): ")
            hora = None
            if hora_input:
                try:
                    hora = datetime.strptime(hora_input, "%H:%M").time()  
                except ValueError:
                    print("Formato de hora inválido. Use HH:MM.")
            
            modulo = input('Digite o nome do módulo (ou deixe em branco): ')
            assunto = input('Digite o nome do assunto (ou deixe em branco): ')
            nome_professor = input('Digite o nome do professor (ou deixe em branco): ').title()

            return trilha, data, hora, modulo, assunto, nome_professor
        except Exception as e:
            print(f'Erro ao aplicar filtros: {e}')
            return None, None, None, None, None, None

    def buscar_encontros_com_filtros(self, trilha=None, data=None, hora=None, modulo=None, assunto=None, nome_professor=None):
        with self.repository.get_session() as session:
            try:
                query = session.query(Encontro).join(Professor)

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

                encontros_filtrados = query.all()

                if encontros_filtrados:
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

                    escolha = int(input("\nDigite o ID do encontro que deseja visualizar: "))
                    encontro_selecionado = next((encontro for encontro in encontros_filtrados if encontro.id == escolha), None)

                    if encontro_selecionado:
                        print(f"\nEncontro selecionado: ID {encontro_selecionado.id}")
                        return encontro_selecionado.id
                    else:
                        print("ID de encontro inválido.")
                        return None

            except Exception as e:
                print(f"Erro ao buscar encontros: {e}")
                return None

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

                df_presenca = pd.DataFrame(lista_presenca)
                print(f'\nPresença dos aspirantes: ')
                print(df_presenca)

                return df_presenca  # Retorna o DataFrame atualizado com a presença

            except Exception as e:
                print(f"Erro ao calcular a presença: {e}")
                return pd.DataFrame()  # Retorna um DataFrame vazio em caso de erro
