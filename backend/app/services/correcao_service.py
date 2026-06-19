import json
from typing import Dict, List, Tuple, Optional
from sqlalchemy.orm import Session

from app.models.gabarito import Gabarito
from app.models.resultado import Resultado


def buscar_gabarito_oficial(db: Session, prova_id: int) -> Dict[str, str]:
    """
    Busca o gabarito oficial de uma prova no banco.
    Retorna {"1": "A", "2": "C", ...}
    """
    itens = db.query(Gabarito).filter(Gabarito.prova_id == prova_id).all()
    return {str(item.questao_numero): item.resposta_correta for item in itens}


def comparar_respostas(
    respostas_aluno: Dict[str, str],
    gabarito_oficial: Dict[str, str]
) -> Tuple[int, int, List[str], List[str]]:
    """
    Compara as respostas do aluno com o gabarito oficial.

    Retorna: (total_acertos, total_questoes, lista_acertos, lista_erros)
    Questões sem resposta do aluno contam como erro.
    """
    acertos = []
    erros = []

    for numero, resposta_correta in gabarito_oficial.items():
        resposta_aluno = respostas_aluno.get(numero)

        if resposta_aluno is not None and resposta_aluno.upper() == resposta_correta:
            acertos.append(numero)
        else:
            erros.append(numero)

    return len(acertos), len(gabarito_oficial), acertos, erros


def calcular_nota(
    total_acertos: int,
    total_questoes: int,
    nota_maxima: float = 10.0
) -> float:
    """Calcula a nota proporcional ao número de acertos."""
    if total_questoes == 0:
        return 0.0
    return round((total_acertos / total_questoes) * nota_maxima, 2)


def gerar_resultado(
    db: Session,
    aluno_id: int,
    prova_id: int,
    respostas_aluno: Dict[str, str]
) -> Resultado:
    """
    Pipeline completo de correção:
    1. Busca o gabarito oficial
    2. Compara com as respostas do aluno
    3. Calcula a nota
    4. Persiste o resultado no banco
    """
    gabarito_oficial = buscar_gabarito_oficial(db, prova_id)

    total_acertos, total_questoes, _, _ = comparar_respostas(
        respostas_aluno, gabarito_oficial
    )
    nota = calcular_nota(total_acertos, total_questoes)

    resultado = Resultado(
        aluno_id=aluno_id,
        prova_id=prova_id,
        respostas_json=json.dumps(respostas_aluno),
        nota=nota,
        total_acertos=total_acertos,
        editado_professor=False,
    )
    db.add(resultado)
    db.commit()
    db.refresh(resultado)

    return resultado


def editar_resultado(
    db: Session,
    resultado: Resultado,
    novas_respostas: Optional[Dict[str, str]] = None,
    nova_nota: Optional[float] = None,
) -> Resultado:
    """
    Permite que o professor corrija manualmente um resultado.
    Use 'novas_respostas' para recalcular a partir de novas marcações,
    ou 'nova_nota' para definir a nota diretamente (ex: questão anulada).
    """
    if novas_respostas is not None:
        gabarito_oficial = buscar_gabarito_oficial(db, resultado.prova_id)
        total_acertos, total_questoes, _, _ = comparar_respostas(
            novas_respostas, gabarito_oficial
        )
        resultado.respostas_json = json.dumps(novas_respostas)
        resultado.total_acertos = total_acertos
        resultado.nota = calcular_nota(total_acertos, total_questoes)

    elif nova_nota is not None:
        resultado.nota = nova_nota

    resultado.editado_professor = True
    db.commit()
    db.refresh(resultado)

    return resultado