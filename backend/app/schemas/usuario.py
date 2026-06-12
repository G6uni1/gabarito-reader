from pydantic import BaseModel, EmailStr
from datetime import datetime
from app.models.usuario import PerfilUsuario


# Dados necessários para criar um usuário
class UsuarioCreate(BaseModel):
    nome: str
    email: EmailStr        # Valida formato de email automaticamente
    senha: str
    perfil: PerfilUsuario = PerfilUsuario.ALUNO


# Dados retornados pela API (nunca expõe a senha!)
class UsuarioResponse(BaseModel):
    id: int
    nome: str
    email: str
    perfil: PerfilUsuario
    ativo: bool
    criado_em: datetime

    class Config:
        from_attributes = True  # Permite converter objeto SQLAlchemy → Pydantic