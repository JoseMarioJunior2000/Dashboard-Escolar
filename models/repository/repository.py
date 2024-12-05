from models.configs.connection import DataBaseConnection

class Repository:
    
    def __init__(self):
        self.db = DataBaseConnection()
        self.db.get_engine()  # Configura o engine
        
    def __enter__(self):
        self.db.__enter__()  # Inicializa a sessão
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is not None:
            self.db.session.rollback()  # Faz rollback em caso de erro
        else:
            self.db.session.commit()  # Comita caso contrário
        self.db.session.close()  # Fecha a sessão

    def get_session(self):
        return self.db.session  # Retorna a sessão