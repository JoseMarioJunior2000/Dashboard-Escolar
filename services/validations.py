import re
import pandas as pd
from datetime import datetime, time
import base64
from flask import jsonify
import hashlib

def turma_slug(turma_id):
    """Gera um slug único para o ID da turma."""
    return hashlib.md5(str(turma_id).encode()).hexdigest()

def encontro_slug(id_encontro):
    """Gera um slug único para o ID do encontro."""
    return hashlib.md5(str(id_encontro).encode()).hexdigest()

def validar_dados_turma(nome: str, data: str, processo: str):
    """
    Função para validar os dados da turma.
    Retorna uma mensagem de erro ou None se não houver erros.
    """

    # Verificar se os campos estão preenchidos
    if not nome or not data or not processo:
        return "Todos os campos obrigatórios devem ser preenchidos."

    # Validar o nome (permitir espaços e caracteres com acentos)
    if not all(c.isalpha() or c.isspace() for c in nome):
        return "O nome só pode conter letras e espaços."

    # Validar o processo (deve ser um número inteiro positivo)
    if not processo.isdigit() or int(processo) <= 0:
        return "O processo seletivo deve ser um número inteiro positivo."

    return None

def validar_dados_aspirante(nome: str, email: str, idade: int, sexo: str, uf: str, fone: str):

    """Função para validar os dados do aspirante. Retorna uma mensagem de erro ou None se não houver erros."""

    if not nome or not email or not idade or not sexo or not uf or not fone:
        return "Todos os campos obrigatórios devem ser preenchidos."
    elif not nome.isalpha():
        return "O nome não pode conter números ou caracteres especiais."
    elif not idade.isdigit() or int(idade) < 0:
        return "A idade deve ser um número positivo."
    
    telefone_pattern = r'^\(\d{2}\) \d{4,5}-\d{4}$'
    if not re.match(telefone_pattern, fone):
        return "Número de telefone inválido. Use o formato (XX) XXXX-XXXX ou (XX) XXXXX-XXXX."
    
    return None

def validar_dados_encontro(trilha, data: str, hora: str, modulo: str, assunto: str, duracao: int, id_professor: int):

    """Função para validar os dados do encontro. Retorna uma mensagem de erro ou None se não houver erros."""

    trilhas_validas = {"Hard", "Soft", "Inglês", "ME"}
    
    if trilha not in trilhas_validas:
        return "Trilha inválida. Escolha uma das opções disponíveis."
    if not data:
        return "A data é obrigatória."
    if not hora:
        return "A hora é obrigatória."
    if not modulo:
        return "O módulo é obrigatório."
    
    # Verificar o comprimento dos campos (caso necessário)
    if len(modulo) > 100:
        return "O módulo não pode ter mais de 50 caracteres."
    if len(assunto) > 100:
        return "O assunto não pode ter mais de 100 caracteres."

    # Converte duracao e id_professor para string antes de verificar com isdigit()
    if not str(duracao).isdigit() or int(duracao) <= 0:
        return "A duração deve ser um número positivo."
    if not str(id_professor).isdigit():
        return "O ID do professor deve ser um número."

    return None  # Retorna None se não houver erros

def converter_data(data):
    """Função para verificar se o valor de data é um Timestamp do Pandas."""
    """Se sim, retornar a data como um objeto date do python."""
    """Se não, tenta converter a string para um objeto date."""

    try:
        # Se for Timestamp, converta para string no formato 'YYYY-MM-DD' antes de passar para strptime
        if isinstance(data, pd.Timestamp):
            data = data.strftime("%Y-%m-%d")  # Converte para string no formato AAAA-MM-DD
        
        # Agora tenta converter a string para um objeto date
        return datetime.strptime(data, "%Y-%m-%d").date()  # Formato AAAA-MM-DD
    except ValueError:
        print("Formato de data inválido. Certifique-se de usar AAAA-MM-DD.")
        return None

def converter_hora(hora):
    """Função para verificar o valor de hora e tratar conforme tipo de dado."""
    if isinstance(hora, pd.Timestamp):
        return hora.time()  # Retorna o objeto time diretamente
    elif isinstance(hora, time):
        return hora  # Retorna diretamente se já for um objeto time
    elif isinstance(hora, str):
        return datetime.strptime(hora, '%H:%M').time()  # Converte para Time se for uma string
    else:
        print(f"Tipo inesperado para hora: {type(hora)}")  # Log de tipo inesperado
        return None  # Retorna None se o tipo não for esperado
    
def foto_to_base64(foto_binaria):
        """Converte foto binária em base64 para exibição."""
        return base64.b64encode(foto_binaria).decode('utf-8') if foto_binaria else None