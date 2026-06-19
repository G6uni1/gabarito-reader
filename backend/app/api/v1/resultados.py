import json
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.api.deps import get_usuario_atual, get_professor_atual
from app.models.usuario import Usuario, PerfilUsuario
from app.models.resultado import Resultado
from app.schemas.resultado import (
    RespostasSubmissao,
    ResultadoResponse,
    ResultadoDetalheResponse,
    ResultadoEdicaoProfessor,
)
from app.services.correcao_service import (
    gerar_resultado,
    editar_resultado,
    buscar_gabarito_oficial,
    comparar_respostas,
)

router = APIRouter()


@router.post("", response_model=ResultadoResponse, status_code=201)
def corrigir_prova(
    dados: RespostasSubmissao,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(get_usuario_atual)
):
    """
    Corrige uma prova a partir das respostas fornecidas.
    Na Etapa 10, isso será chamado automaticamente após a leitura da foto.
    """
    return gerar_resultado(db, dados.aluno_id, dados.prova_id, dados.respostas)


@router.get("", response_model=List[ResultadoResponse])
def listar_resultados(
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(get_usuario_atual)
):
    """Aluno vê apenas seus resultados; professor/admin vê todos."""
    query = db.query(Resultado)

    if usuario_atual.perfil == PerfilUsuario.ALUNO:
        query = query.filter(Resultado.aluno_id == usuario_atual.id)

    return query.all()


@router.get("/{resultado_id}", response_model=ResultadoDetalheResponse)
def detalhar_resultado(
    resultado_id: int,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(get_usuario_atual)
):
    """Retorna o detalhe de um resultado, com acertos e erros por questão."""
    resultado = db.query(Resultado).filter(Resultado.id == resultado_id).first()

    if not resultado:
        raise HTTPException(status_code=404, detail="Resultado não encontrado")

    if usuario_atual.perfil == PerfilUsuario.ALUNO and resultado.aluno_id != usuario_atual.id:
        raise HTTPException(status_code=403, detail="Acesso não permitido")

    respostas_aluno = json.loads(resultado.respostas_json)
    gabarito_oficial = buscar_gabarito_oficial(db, resultado.prova_id)
    _, _, acertos, erros = comparar_respostas(respostas_aluno, gabarito_oficial)

    base = ResultadoResponse.model_validate(resultado)
    return ResultadoDetalheResponse(
        **base.model_dump(),
        respostas_aluno=respostas_aluno,
        acertos=acertos,
        erros=erros,
    )


@router.put("/{resultado_id}", response_model=ResultadoResponse)
def editar_resultado_professor(
    resultado_id: int,
    dados: ResultadoEdicaoProfessor,
    db: Session = Depends(get_db),
    professor: Usuario = Depends(get_professor_atual)
):
    """Permite ao professor corrigir manualmente um resultado."""
    resultado = db.query(Resultado).filter(Resultado.id == resultado_id).first()

    if not resultado:
        raise HTTPException(status_code=404, detail="Resultado não encontrado")

    if dados.novas_respostas is None and dados.nova_nota is None:
        raise HTTPException(
            status_code=400,
            detail="Envie 'novas_respostas' ou 'nova_nota'"
        )

    return editar_resultado(
        db, resultado,
        novas_respostas=dados.novas_respostas,
        nova_nota=dados.nova_nota,
    )