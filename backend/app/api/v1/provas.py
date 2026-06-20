import os
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.api.deps import get_usuario_atual, get_professor_atual
from app.models.usuario import Usuario
from app.models.prova import Prova
from app.models.gabarito import Gabarito
from app.schemas.prova import ProvaCreate, ProvaResponse
from app.services.folha_service import gerar_folha_aluno, salvar_folha
from app.models.usuario import Usuario as UsuarioModel

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
    """Cria uma nova prova junto com seu gabarito oficial."""
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

    for numero_str, resposta in dados.gabarito.items():
        db.add(Gabarito(
            prova_id=nova_prova.id,
            questao_numero=int(numero_str),
            resposta_correta=resposta.upper(),
        ))

    db.commit()
    return nova_prova


@router.get("/{prova_id}/folha/{aluno_id}")
def gerar_folha_resposta(
    prova_id: int,
    aluno_id: int,
    db: Session = Depends(get_db),
    professor: Usuario = Depends(get_professor_atual)
):
    """Gera e retorna a folha de resposta para um aluno específico."""
    prova = db.query(Prova).filter(Prova.id == prova_id).first()
    if not prova:
        raise HTTPException(status_code=404, detail="Prova não encontrada")

    aluno = db.query(UsuarioModel).filter(UsuarioModel.id == aluno_id).first()
    if not aluno:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")

    folha = gerar_folha_aluno(
        aluno_id=aluno.id,
        aluno_nome=aluno.nome,
        prova_id=prova.id,
        prova_titulo=prova.titulo,
        total_questoes=prova.total_questoes,
    )

    caminho = f"uploads/folha_prova{prova_id}_aluno{aluno_id}.png"
    salvar_folha(folha, caminho)

    return FileResponse(
        caminho,
        media_type="image/png",
        filename=f"folha_{aluno.nome.replace(' ', '_')}.png"
    )