from sqlalchemy import Integer, BigInteger, ForeignKey, Table, Column, Boolean, String, Date, Time, VARCHAR, PrimaryKeyConstraint
from sqlalchemy.orm import relationship, mapped_column, Mapped
from models.configs.base import Base
from typing import List

# Tabela associativa entre Encontro e Aspirante
encontro_aspirantes = Table(
    'encontro_aspirantes',
    Base.metadata,
    Column('encontro_id', BigInteger, ForeignKey('encontro.id'), primary_key=True),
    Column('aspirante_id', BigInteger, ForeignKey('aspirante.id'), primary_key=True),
    Column('minuto', Integer()),
    PrimaryKeyConstraint('encontro_id', 'aspirante_id')
)

class Encontro(Base):
    __tablename__ = 'encontro'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    trilha: Mapped[str] = mapped_column(String)
    data: Mapped[Date] = mapped_column(Date) 
    hora: Mapped[Time] = mapped_column(Time) 
    modulo: Mapped[str] = mapped_column(VARCHAR(255))
    assunto: Mapped[str] = mapped_column(VARCHAR(255), nullable=True)
    duracao: Mapped[int] = mapped_column(Integer)
    id_professor: Mapped[int] = mapped_column(Integer, ForeignKey('professor.id'))
    atividade: Mapped[bool] = mapped_column(Boolean)
    meetingId: Mapped[int] = mapped_column(Integer, nullable=True)

    # Relacionamento com a tabela aspirantes usando a tabela associativa
    aspirantes = relationship('Aspirante', secondary=encontro_aspirantes, backref='encontros')

    def __repr__(self):
        return f'ID: {self.id}\n' \
               f'Trilha: {self.trilha}\n' \
               f'Data: {self.data}\n' \
               f'Hora: {self.hora}\n' \
               f'Módulo: {self.modulo}\n' \
               f'Assunto: {self.assunto}\n' \
               f'Duração: {self.duracao}\n' \
               f'Id do Professor: {self.id_professor}\n' \
               f'Atividade: {self.atividade}'

