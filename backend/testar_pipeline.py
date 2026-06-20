"""
Testa o pipeline completo sem precisar do servidor.
Execute: python testar_pipeline.py uploads/folha_preenchida.png 1
                                    ^caminho da imagem          ^prova_id
"""
import sys
import cv2
import numpy as np

from app.vision.preprocessamento import preprocessar_imagem, carregar_imagem
from app.vision.leitor_qrcode import ler_qrcode_com_fallback
from app.vision.detector_respostas import detectar_todas_respostas


def testar_pipeline_local(caminho: str, prova_id: int):
    print("\n" + "="*50)
    print("TESTE DO PIPELINE COMPLETO")
    print("="*50)

    # Passo 1 — Carregar imagem
    print("\n[1/4] Carregando imagem...")
    imagem = carregar_imagem(caminho)
    if imagem is None:
        print("❌ Imagem não encontrada")
        return
    print(f"✅ Imagem carregada: {imagem.shape[1]}x{imagem.shape[0]}px")

    # Passo 2 — Identificar aluno
    print("\n[2/4] Identificando aluno pelo QR Code...")
    aluno_id = ler_qrcode_com_fallback(imagem)
    if aluno_id:
        print(f"✅ Aluno identificado: ID = {aluno_id}")
    else:
        print("⚠️  QR Code não encontrado")
        print("   → Em produção, isso bloquearia o processamento")
        print("   → Continuando para testar a detecção de respostas...")

    # Passo 3 — Pré-processar
    print("\n[3/4] Pré-processando imagem...")
    imagem_processada, status = preprocessar_imagem(caminho)
    if imagem_processada is None:
        print(f"❌ Erro no pré-processamento: {status}")
        return
    print(f"✅ Pré-processamento concluído")

    # Passo 4 — Detectar respostas
    print("\n[4/4] Detectando respostas...")
    resultado = detectar_todas_respostas(imagem_processada)

    print(f"\n{'='*50}")
    print("RESULTADO:")
    print(f"{'='*50}")
    print(f"Respostas detectadas: {resultado['total_detectadas']}")

    for questao, resposta in resultado["respostas"].items():
        print(f"  Q{questao:>2}: {resposta}")

    if resultado["questoes_invalidas"]:
        print(f"\n⚠️  Questões sem resposta: {resultado['questoes_invalidas']}")

    print(f"\n→ Prova ID: {prova_id}")
    print(f"→ Aluno ID: {aluno_id or 'não identificado'}")
    print(f"\nEm produção, esses dados seriam salvos no banco automaticamente.")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python testar_pipeline.py <imagem> <prova_id>")
        print("Ex:  python testar_pipeline.py uploads/folha_preenchida.png 1")
    else:
        testar_pipeline_local(sys.argv[1], int(sys.argv[2]))