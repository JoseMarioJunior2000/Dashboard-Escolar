from sqlalchemy import Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship, mapped_column, Mapped
from models.configs.base import Base

class Atividade(Base):
    __tablename__ = 'atividade'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    id_encontro: Mapped[int] = mapped_column(Integer, ForeignKey('encontro.id'),)
    id_aspirante: Mapped[int] = mapped_column(Integer, ForeignKey('aspirante.id'))
    entrega: Mapped[bool] = mapped_column(Boolean)
    atraso: Mapped[int] = mapped_column(Integer, nullable=True)
    notas: Mapped[int] = mapped_column(Integer, nullable=True)


    def __repr__(self):
        return f'ID: {self.id}\n' \
               f'ID do Encontro: {self.id_encontro}\n' \
               f'ID do Aspirante: {self.id_aspirante}\n' \
               f'Entrega: {self.entrega}\n' \
               f'Atraso: {self.atraso}\n' \
               f'Notas: {self.notas}'