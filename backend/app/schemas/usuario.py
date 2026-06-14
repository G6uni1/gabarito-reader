from pydantic import BaseModel, EmailStr
from datetime import datetime
from app.models.usuario import PerfilUsuario


class UsuarioCreate(BaseModel):
    nome: str
    email: EmailStr
    senha: str
    perfil: PerfilUsuario = PerfilUsuario.ALUNO


class UsuarioResponse(BaseModel):
    id: int
    nome: str
    email: str
    perfil: PerfilUsuario
    ativo: bool
    criado_em: datetime

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    email: EmailStr
    senha: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    perfil: PerfilUsuario
    nome: str