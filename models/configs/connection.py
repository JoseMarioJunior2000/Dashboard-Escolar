import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.configs.base import Base

class DataBaseConnection:
    def __init__(self, db_name: str = 'db.db') -> None:
        try:
            # Constrói a string de conexão para SQLite
            self.__conection_string = f"sqlite:///{db_name}"
            
            # Cria o engine usando o SQLite
            self.__engine = self.__create_database_engine()
            if self.__engine:
                print(f'INFO: Conectado ao banco de dados SQLite: {db_name}')

            self.session = None
        
        except Exception as e:
            print(f'INFO: Falha ao conectar ao banco de dados SQLite: {e}')

    def __create_database_engine(self):
        # Cria o engine com a string de conexão para SQLite
        engine = create_engine(self.__conection_string)
        return engine
    
    def get_engine(self):
        return self.__engine
    
    def __create_tables(self):
        import models.entities.__all_entities
        Base.metadata.create_all(self.__engine)
    
    def __enter__(self):
        self.__create_tables()  # Chama o método para criar as tabelas
        session_make = sessionmaker(bind=self.__engine)
        self.session = session_make()
        
        if not self.session:
            raise Exception("Falha ao criar a sessão com o banco de dados.")

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.session.rollback()  # Faz rollback em caso de exceção
        else:
            self.session.commit()  # Faz commit em caso de sucesso
        self.session.close()  # Fecha a sessão

