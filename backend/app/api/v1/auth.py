from fastapi import APIRouter

router = APIRouter()


@router.post("/login")
def login():
    # Implementado na Etapa 5
    return {"mensagem": "Rota de login — em breve"}


@router.post("/cadastro")
def cadastro():
    # Implementado na Etapa 5
    return {"mensagem": "Rota de cadastro — em breve"}