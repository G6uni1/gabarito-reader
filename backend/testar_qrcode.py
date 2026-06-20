"""
Testa geração e leitura do QR Code.
Execute: python testar_qrcode.py
"""
import cv2
from app.vision.leitor_qrcode import (
    gerar_conteudo_qrcode,
    extrair_aluno_id,
    ler_qrcode_com_fallback
)
from app.services.folha_service import gerar_folha_aluno, salvar_folha


def testar_qrcode():
    print("="*50)
    print("TESTE DE QR CODE")
    print("="*50)

    # 1. Gera uma folha com QR Code do aluno ID=1
    print("\n1. Gerando folha com QR Code...")
    folha = gerar_folha_aluno(
        aluno_id=1,
        aluno_nome="João da Silva",
        prova_id=1,
        prova_titulo="Matemática - Turma A"
    )
    salvar_folha(folha, "uploads/folha_qrcode_teste.png")
    print("   ✅ Folha salva em uploads/folha_qrcode_teste.png")

    # 2. Lê a folha gerada e tenta encontrar o QR Code
    print("\n2. Lendo QR Code da folha gerada...")
    imagem = cv2.imread("uploads/folha_qrcode_teste.png")
    aluno_id = ler_qrcode_com_fallback(imagem)

    if aluno_id is not None:
        print(f"   ✅ Aluno identificado! ID = {aluno_id}")
    else:
        print("   ❌ QR Code não encontrado")

    # 3. Exibe a folha gerada
    print("\n3. Exibindo folha...")
    cv2.imshow("Folha com QR Code", folha)
    print("   Pressione qualquer tecla para fechar...")
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    testar_qrcode()