from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ItemCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, examples=["Notebook"])
    description: Optional[str] = Field(None, max_length=500, examples=["Notebook Dell 16GB"])
    active: bool = Field(True)


class ItemOut(ItemCreate):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
