from sqlalchemy import Integer, VARCHAR, ForeignKey, Column, Table, BigInteger, LargeBinary, Boolean, PrimaryKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.configs.base import Base
from typing import List
from models.entities.turma import Turma


turmas_aspirantes = Table(
    'matricula',
    Base.metadata,
    Column('turma_id', Integer, ForeignKey('turma.id')),
    Column('aspirante_id', BigInteger, ForeignKey('aspirante.id')),
    PrimaryKeyConstraint('turma_id', 'aspirante_id')
)

class Aspirante(Base):
    __tablename__ = 'aspirante'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome: Mapped[str] = mapped_column(VARCHAR(255))
    email: Mapped[str] = mapped_column(VARCHAR(255))
    idade: Mapped[str] = mapped_column(VARCHAR(10))
    sexo: Mapped[str] = mapped_column(VARCHAR(10))
    uf: Mapped[str] = mapped_column(VARCHAR(2))
    fone: Mapped[str] = mapped_column(VARCHAR(15))
    ativo: Mapped[bool] = mapped_column(Boolean)
    aspirantld: Mapped[int] = mapped_column(BigInteger, nullable=True)
    foto: Mapped[bytes] = mapped_column(LargeBinary, nullable=True)

    turmas: Mapped[List['Turma']] = relationship('Turma', secondary=turmas_aspirantes, backref='aspirantes')
