from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.database.database import Base


# Enum garante que só valores válidos sejam inseridos
class PerfilUsuario(str, enum.Enum):
    ALUNO = "aluno"
    PROFESSOR = "professor"
    ADMIN = "admin"


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    senha_hash = Column(String(255), nullable=False)
    perfil = Column(Enum(PerfilUsuario), default=PerfilUsuario.ALUNO, nullable=False)
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())

    # Relacionamentos
    provas_criadas = relationship("Prova", back_populates="professor")
    resultados = relationship("Resultado", back_populates="aluno")

    def __repr__(self):
        return f"<Usuario {self.email} ({self.perfil})>"