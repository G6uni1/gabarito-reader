from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.config import settings
from app.models.usuario import Usuario, PerfilUsuario
from app.schemas.usuario import UsuarioCreate

# Contexto de criptografia — define o algoritmo de hash
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ─── Funções de senha ────────────────────────────────────────────────────────

def hash_senha(senha: str) -> str:
    """Transforma a senha em hash bcrypt."""
    return pwd_context.hash(senha)


def verificar_senha(senha_pura: str, senha_hash: str) -> bool:
    """Compara a senha digitada com o hash salvo no banco."""
    return pwd_context.verify(senha_pura, senha_hash)


# ─── Funções de JWT ──────────────────────────────────────────────────────────

def criar_token(dados: dict, expira_em: Optional[timedelta] = None) -> str:
    """Gera um token JWT com os dados fornecidos."""
    payload = dados.copy()

    if expira_em:
        expiracao = datetime.utcnow() + expira_em
    else:
        expiracao = datetime.utcnow() + timedelta(minutes=30)

    payload.update({"exp": expiracao})

    token = jwt.encode(
        payload,
        settings.secret_key,
        algorithm=settings.algorithm
    )
    return token


def decodificar_token(token: str) -> Optional[dict]:
    """Decodifica e valida um token JWT. Retorna None se inválido."""
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )
        return payload
    except JWTError:
        return None


# ─── Operações de usuário ────────────────────────────────────────────────────

def buscar_usuario_por_email(db: Session, email: str) -> Optional[Usuario]:
    """Busca um usuário pelo email."""
    return db.query(Usuario).filter(Usuario.email == email).first()


def buscar_usuario_por_id(db: Session, usuario_id: int) -> Optional[Usuario]:
    """Busca um usuário pelo ID."""
    return db.query(Usuario).filter(Usuario.id == usuario_id).first()


def criar_usuario(db: Session, dados: UsuarioCreate) -> Usuario:
    """Cria um novo usuário no banco com a senha hasheada."""
    novo_usuario = Usuario(
        nome=dados.nome,
        email=dados.email,
        senha_hash=hash_senha(dados.senha),
        perfil=dados.perfil,
    )
    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)  # Atualiza o objeto com os dados gerados pelo banco (id, criado_em)
    return novo_usuario


def autenticar_usuario(db: Session, email: str, senha: str) -> Optional[Usuario]:
    """Verifica email e senha. Retorna o usuário se válido, None se não."""
    usuario = buscar_usuario_por_email(db, email)
    if not usuario:
        return None
    if not verificar_senha(senha, usuario.senha_hash):
        return None
    return usuario