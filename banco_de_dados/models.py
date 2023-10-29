from sqlalchemy import Column, Integer, String, Numeric, ForeignKey
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass

class Cliente(Base):
    __tablename__ = 'cliente'

    id = Column(Integer, primary_key=True)
    nome = Column(String(255), nullable=False)
    cpf = Column(String(11), nullable=False)
    endereço = Column(String(255), nullable=False)


class Conta(Base):
    __tablename__ = 'conta'

    id = Column(Integer, primary_key=True)
    id_cliente = Column(Integer, ForeignKey('cliente.id'))
    tipo = Column(String(10), nullable=False)
    agencia = Column(Integer, nullable=False)
    num = Column(Integer, nullable=False)
    saldo = Column(Numeric(15, 2), nullable=False)
