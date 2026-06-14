from fastapi import APIRouter, Depends

from app.api.deps import get_usuario_atual, get_professor_atual
from app.models.usuario import Usuario

router = APIRouter()


@router.get("")
def listar_provas(usuario_atual: Usuario = Depends(get_usuario_atual)):
    """
    Rota protegida — qualquer usuário autenticado pode ver.
    Implementação completa na Etapa 8.
    """
    return {"mensagem": "Listagem de provas — em breve", "usuario": usuario_atual.nome}


@router.post("")
def criar_prova(professor: Usuario = Depends(get_professor_atual)):
    """
    Rota protegida — apenas professores podem criar provas.
    Implementação completa na Etapa 8.
    """
    return {"mensagem": "Criação de prova — em breve", "professor": professor.nome}