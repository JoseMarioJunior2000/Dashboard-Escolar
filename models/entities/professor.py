from sqlalchemy import VARCHAR, Integer
from sqlalchemy.orm import Mapped, mapped_column
from models.configs.base import Base

class Professor(Base):
    __tablename__: str = 'professor'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome: Mapped[str] = mapped_column(VARCHAR(255))
    trilha: Mapped[str] = mapped_column(VARCHAR(7))

    def __repr__(self):
        return f'ID: {self.id}\n' \
               f'Nome: {self.nome}\n' \
               f'Trilha: {self.trilha}'