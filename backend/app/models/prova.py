from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.database import Base


class Prova(Base):
    __tablename__ = "provas"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(200), nullable=False)
    descricao = Column(Text, nullable=True)
    total_questoes = Column(Integer, nullable=False, default=25)
    professor_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    criada_em = Column(DateTime(timezone=True), server_default=func.now())
    ativa = Column(Boolean, default=True)

    # Relacionamentos
    professor = relationship("Usuario", back_populates="provas_criadas")
    gabarito = relationship("Gabarito", back_populates="prova", uselist=False)
    resultados = relationship("Resultado", back_populates="prova")

    def __repr__(self):
        return f"<Prova {self.titulo}>"