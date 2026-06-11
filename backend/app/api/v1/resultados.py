from fastapi import APIRouter

router = APIRouter()


@router.get("")
def listar_resultados():
    # Implementado na Etapa 8
    return {"mensagem": "Listagem de resultados — em breve"}