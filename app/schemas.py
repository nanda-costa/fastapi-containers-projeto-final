from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field


class ProjetoCreate(BaseModel):
    nome_projeto: str = Field(
        ..., min_length=2, max_length=150, examples=["PD&I Track 2024"]
    )
    data_inicio: date = Field(..., examples=["2025-01-01"])
    data_fim: Optional[date] = Field(None, examples=["2025-12-31"])


class ProjetoOut(ProjetoCreate):
    id: int

    model_config = {"from_attributes": True}


class ItemCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, examples=["Notebook"])
    description: Optional[str] = Field(
        None, max_length=500, examples=["Notebook Dell 16GB"]
    )
    active: bool = Field(True)
    idprojeto: Optional[int] = Field(None, examples=[1])


class ItemOut(ItemCreate):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class StudentCreate(BaseModel):
    name: str = Field(
        ..., min_length=2, max_length=100, examples=["Juliana Fernanda Felix"]
    )
    cpf: str = Field(..., min_length=11, max_length=14, examples=["000.000.000-00"])
    data_inicio_lab: date = Field(..., examples=["2025-03-01"])
    data_fim_lab: Optional[date] = Field(None, examples=["2025-12-31"])


class StudentOut(StudentCreate):
    id: int
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class WithdrawalCreate(BaseModel):
    item_id: int = Field(..., examples=[1])
    cpf: str = Field(..., min_length=11, max_length=14, examples=["000.000.000-00"])


class WithdrawalOut(BaseModel):
    id: int
    item: ItemOut
    student: StudentOut
    withdrawn_at: datetime
    devolvido_em: Optional[datetime] = None

    model_config = {"from_attributes": True}