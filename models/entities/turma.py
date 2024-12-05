from sqlalchemy import Integer, VARCHAR, Date
from sqlalchemy.orm import Mapped, mapped_column
from models.configs.base import Base

class Turma(Base):
    __tablename__ = 'turma'

    id: Mapped[int] = mapped_column(Integer, primary_key=True) 
    nome: Mapped[str] = mapped_column(VARCHAR(255))
    data: Mapped[Date] = mapped_column(Date)   
    processo: Mapped[int] = mapped_column(Integer)   

    def __repr__(self):
        return f'ID: {self.id}\n' \
               f'Nome da Truma: {self.nome}\n' \
               f'Data de Criação da Turma: {self.data}\n' \
               f'Número do Processo Seletivo: {self.processo}'