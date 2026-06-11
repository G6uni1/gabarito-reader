from fastapi import APIRouter

router = APIRouter()


@router.get("")
def listar_provas():
    # Implementado na Etapa 4
    return {"mensagem": "Listagem de provas — em breve"}


@router.post("")
def criar_prova():
    # Implementado na Etapa 4
    return {"mensagem": "Criação de prova — em breve"}