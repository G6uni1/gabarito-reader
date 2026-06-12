from sqlalchemy import Column, Integer, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.database import Base


class Resultado(Base):
    __tablename__ = "resultados"

    id = Column(Integer, primary_key=True, index=True)
    aluno_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    prova_id = Column(Integer, ForeignKey("provas.id"), nullable=False)

    # Respostas detectadas salvas como JSON string
    # Ex: '{"1": "A", "2": "C", "3": "D"}'
    respostas_json = Column(Text, nullable=False)

    nota = Column(Float, nullable=False)
    total_acertos = Column(Integer, nullable=False)
    corrigido_em = Column(DateTime(timezone=True), server_default=func.now())
    editado_professor = Column(Boolean, default=False)

    # Relacionamentos
    aluno = relationship("Usuario", back_populates="resultados")
    prova = relationship("Prova", back_populates="resultados")

    def __repr__(self):
        return f"<Resultado aluno={self.aluno_id} prova={self.prova_id} nota={self.nota}>"