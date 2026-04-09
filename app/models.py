from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import relationship

from app.database import Base


class Projeto(Base):
    __tablename__ = "projetos"

    id = Column(Integer, primary_key=True, index=True)
    nome_projeto = Column(String(150), nullable=False)
    data_inicio = Column(Date, nullable=False)
    data_fim = Column(Date, nullable=True)

    items = relationship("Item", back_populates="projeto")


class Student(Base):
    __tablename__ = "bolsistas"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    cpf = Column(String(14), unique=True, nullable=False, index=True)
    data_inicio_lab = Column(Date, nullable=False)
    data_fim_lab = Column(Date, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    withdrawals = relationship("Withdrawal", back_populates="student")


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)
    active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    idprojeto = Column(
        Integer, ForeignKey("projetos.id", ondelete="SET NULL"), nullable=True
    )

    projeto = relationship("Projeto", back_populates="items")
    withdrawals = relationship("Withdrawal", back_populates="item")


class Withdrawal(Base):
    __tablename__ = "retiradas"

    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("bolsistas.id"), nullable=False)
    withdrawn_at = Column(DateTime(timezone=True), server_default=func.now())
    devolvido_em = Column(DateTime(timezone=True), nullable=True)

    item = relationship("Item", back_populates="withdrawals")
    student = relationship("Student", back_populates="withdrawals")