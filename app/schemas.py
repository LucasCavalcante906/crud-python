from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class UserBase(BaseModel):
    nome: str = Field(..., min_length=1, max_length=100, examples=["Maria"])
    sobrenome: str = Field(..., min_length=1, max_length=100, examples=["Silva"])
    telefone: str = Field(..., min_length=8, max_length=20, examples=["+55 11 99999-0000"])
    endereco: str = Field(
        ..., min_length=1, max_length=255, examples=["Rua das Flores, 123 - São Paulo/SP"]
    )


class UserCreate(UserBase):
    """Corpo do POST e do PUT: todos os campos são obrigatórios."""


class UserUpdate(BaseModel):
    """Corpo do PATCH: todos os campos são opcionais."""

    nome: str | None = Field(default=None, min_length=1, max_length=100)
    sobrenome: str | None = Field(default=None, min_length=1, max_length=100)
    telefone: str | None = Field(default=None, min_length=8, max_length=20)
    endereco: str | None = Field(default=None, min_length=1, max_length=255)


class UserRead(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    criado_em: datetime
    atualizado_em: datetime
