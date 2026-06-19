from pydantic import BaseModel
from datetime import datetime
from typing import Dict, List, Optional


class RespostasSubmissao(BaseModel):
    """Dados enviados para corrigir uma prova."""
    aluno_id: int
    prova_id: int
    respostas: Dict[str, str]  # {"1": "A", "2": "C", ...}


class ResultadoResponse(BaseModel):
    id: int
    aluno_id: int
    prova_id: int
    nota: float
    total_acertos: int
    corrigido_em: datetime
    editado_professor: bool

    class Config:
        from_attributes = True


class ResultadoDetalheResponse(ResultadoResponse):
    """Resposta detalhada, incluindo quais questões foram acertadas/erradas."""
    respostas_aluno: Dict[str, str]
    acertos: List[str]
    erros: List[str]


class ResultadoEdicaoProfessor(BaseModel):
    """
    Permite ao professor editar manualmente um resultado.
    Envie 'novas_respostas' OU 'nova_nota' (não os dois).
    """
    novas_respostas: Optional[Dict[str, str]] = None
    nova_nota: Optional[float] = None