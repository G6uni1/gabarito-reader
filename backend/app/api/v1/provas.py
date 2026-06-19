from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.api.deps import get_usuario_atual, get_professor_atual
from app.models.usuario import Usuario
from app.models.prova import Prova
from app.models.gabarito import Gabarito
from app.schemas.prova import ProvaCreate, ProvaResponse

router = APIRouter()


@router.get("", response_model=List[ProvaResponse])
def listar_provas(
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(get_usuario_atual)
):
    """Lista todas as provas ativas."""
    return db.query(Prova).filter(Prova.ativa == True).all()


@router.post("", response_model=ProvaResponse, status_code=201)
def criar_prova(
    dados: ProvaCreate,
    db: Session = Depends(get_db),
    professor: Usuario = Depends(get_professor_atual)
):
    """
    Cria uma nova prova junto com seu gabarito oficial.
    Apenas professores e admins podem criar provas.
    """
    if len(dados.gabarito) != dados.total_questoes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"O gabarito deve ter {dados.total_questoes} respostas, "
                f"mas recebeu {len(dados.gabarito)}"
            )
        )

    nova_prova = Prova(
        titulo=dados.titulo,
        descricao=dados.descricao,
        total_questoes=dados.total_questoes,
        professor_id=professor.id,
    )
    db.add(nova_prova)
    db.commit()
    db.refresh(nova_prova)

    # Cria uma linha de gabarito para cada questão
    for numero_str, resposta in dados.gabarito.items():
        db.add(Gabarito(
            prova_id=nova_prova.id,
            questao_numero=int(numero_str),
            resposta_correta=resposta.upper(),
        ))

    db.commit()
    return nova_prova