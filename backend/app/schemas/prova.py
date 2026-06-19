from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional, Dict


class ProvaCreate(BaseModel):
    titulo: str
    descricao: Optional[str] = None
    total_questoes: int = 25
    gabarito: Dict[str, str]  # Ex: {"1": "A", "2": "C", "3": "B"}

    @field_validator("gabarito")
    @classmethod
    def validar_respostas(cls, valor):
        """Garante que cada resposta do gabarito é uma letra válida."""
        alternativas_validas = {"A", "B", "C", "D", "E"}
        for questao, resposta in valor.items():
            if resposta.upper() not in alternativas_validas:
                raise ValueError(
                    f"Resposta inválida na questão {questao}: '{resposta}'"
                )
        return valor


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