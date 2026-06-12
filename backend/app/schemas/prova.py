from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ProvaCreate(BaseModel):
    titulo: str
    descricao: Optional[str] = None
    total_questoes: int = 25


class ProvaResponse(BaseModel):
    id: int
    titulo: str
    descricao: Optional[str]
    total_questoes: int
    professor_id: int
    criada_em: datetime
    ativa: bool

    class Config:
        from_attributes = True