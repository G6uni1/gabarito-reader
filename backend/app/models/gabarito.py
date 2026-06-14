from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.database.database import Base


class Gabarito(Base):
    __tablename__ = "gabaritos"

    id = Column(Integer, primary_key=True, index=True)
    prova_id = Column(Integer, ForeignKey("provas.id"), nullable=False)
    questao_numero = Column(Integer, nullable=False)
    resposta_correta = Column(String(1), nullable=False)  # "A", "B", "C", "D" ou "E"

    # Relacionamento
    prova = relationship("Prova", back_populates="gabarito")

    def __repr__(self):
        return f"<Gabarito Q{self.questao_numero}: {self.resposta_correta}>"