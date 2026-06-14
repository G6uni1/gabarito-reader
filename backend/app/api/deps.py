import token

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.usuario import Usuario, PerfilUsuario
from app.services.auth_service import decodificar_token, buscar_usuario_por_id

# Define o endpoint onde o token é obtido
http_bearer = HTTPBearer()

def get_usuario_atual(
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
    db: Session = Depends(get_db)
) -> Usuario:

    token = credentials.credentials

    print("TOKEN:", token)

    print(type(credentials))
    print(credentials)
    print(token)

    payload = decodificar_token(token)
    print("PAYLOAD:", payload)

    if payload is None:
        raise credenciais_invalidas

    usuario_id = payload.get("sub")
    print("USUARIO_ID:", usuario_id)

    usuario = buscar_usuario_por_id(db, int(usuario_id))
    print("USUARIO:", usuario)

    if usuario is None or not usuario.ativo:
        raise credenciais_invalidas

    return usuario


def get_professor_atual(
    usuario: Usuario = Depends(get_usuario_atual)
) -> Usuario:
    """Exige que o usuário seja professor ou admin."""
    if usuario.perfil not in [PerfilUsuario.PROFESSOR, PerfilUsuario.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso permitido apenas para professores"
        )
    return usuario


def get_admin_atual(
    usuario: Usuario = Depends(get_usuario_atual)
) -> Usuario:
    """Exige que o usuário seja admin."""
    if usuario.perfil != PerfilUsuario.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso permitido apenas para administradores"
        )""
    return usuario