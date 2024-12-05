from sqlalchemy import Integer, BigInteger, ForeignKey, Table, Column, Boolean, String, Date, Time, VARCHAR, PrimaryKeyConstraint
from sqlalchemy.orm import relationship, mapped_column, Mapped
from models.configs.base import Base
from typing import List

# Tabela associativa entre Encontro e Aspirante
evento_aspirantes = Table(
    'evento_aspirantes',
    Base.metadata,
    Column('evento_id', BigInteger, ForeignKey('evento.id')),
    Column('aspirante_id', BigInteger, ForeignKey('aspirante.id')),
)

class Evento(Base):
    __tablename__ = 'evento'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(VARCHAR(100))
    data: Mapped[Date] = mapped_column(Date) 
    hora: Mapped[Time] = mapped_column(Time) 

    # Relacionamento com a tabela aspirantes usando a tabela associativa
    aspirantes = relationship('Aspirante', secondary=evento_aspirantes, backref='evento')

    def __repr__(self):
        return f'ID: {self.id}\n' \
               f'Trilha: {self.nome}\n' \
               f'Data: {self.data}\n' \
               f'Hora: {self.hora}'

