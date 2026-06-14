from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta

from app.database.database import get_db
from app.schemas.usuario import UsuarioCreate, UsuarioResponse, LoginRequest, TokenResponse
from app.services.auth_service import (
    criar_usuario,
    autenticar_usuario,
    buscar_usuario_por_email,
    criar_token,
)
from app.api.deps import get_usuario_atual
from app.config import settings
from app.models.usuario import Usuario

router = APIRouter()


@router.post("/cadastro", response_model=UsuarioResponse, status_code=201)
def cadastro(dados: UsuarioCreate, db: Session = Depends(get_db)):
    """Cria um novo usuário no sistema."""

    # Verifica se o email já está em uso
    if buscar_usuario_por_email(db, dados.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este email já está cadastrado"
        )

    usuario = criar_usuario(db, dados)
    return usuario


@router.post("/login", response_model=TokenResponse)
def login(dados: LoginRequest, db: Session = Depends(get_db)):
    """Autentica o usuário e retorna um token JWT."""

    usuario = autenticar_usuario(db, dados.email, dados.senha)

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Gera o token com o ID do usuário no campo "sub" (subject)
    token = criar_token(
        dados={"sub": str(usuario.id)},
        expira_em=timedelta(minutes=settings.access_token_expire_minutes)
    )

    return TokenResponse(
        access_token=token,
        perfil=usuario.perfil,
        nome=usuario.nome,
    )


@router.get("/me", response_model=UsuarioResponse)
def meu_perfil(usuario_atual: Usuario = Depends(get_usuario_atual)):
    """Retorna os dados do usuário autenticado."""
    return usuario_atual