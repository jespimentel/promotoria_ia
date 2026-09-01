"""Extrai PDFs página por página, com fallback local para Tesseract."""

from __future__ import annotations

import argparse
from contextlib import contextmanager
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

try:
    import pymupdf as fitz
except ImportError as exc:  # pragma: no cover - mensagem operacional
    raise SystemExit(
        "PyMuPDF não está disponível. Execute o script com "
        "'uv run python', a partir da raiz do projeto."
    ) from exc


LIMIAR_CARACTERES = 300
SEPARADOR = "\n\n---\n\n"


@dataclass
class Resultado:
    origem: Path
    destino: Path
    nativas: int = 0
    ocr: int = 0
    pendentes: int = 0


def argumentos() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extrai PDFs para Markdown e usa Tesseract em páginas com menos de 300 caracteres."
    )
    parser.add_argument(
        "pdfs",
        nargs="*",
        type=Path,
        help="PDFs específicos. Sem argumentos, processa input/*.pdf de forma idempotente.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("md"),
        help="Pasta de saída (padrão: md).",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Reprocessa saídas existentes também no modo em lote.",
    )
    parser.add_argument(
        "--lang",
        default="por",
        help="Idioma do Tesseract (padrão: por).",
    )
    parser.add_argument(
        "--dpi",
        type=int,
        default=300,
        help="Resolução usada no OCR (padrão: 300).",
    )
    parser.add_argument(
        "--check-deps",
        action="store_true",
        help="Verifica PyMuPDF, Tesseract e o idioma solicitado, sem processar PDFs.",
    )
    return parser.parse_args()


def executavel_tesseract() -> str | None:
    return shutil.which("tesseract")


def idiomas_tesseract(executavel: str) -> set[str]:
    processo = subprocess.run(
        [executavel, "--list-langs"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if processo.returncode != 0:
        detalhe = (processo.stderr or processo.stdout).strip()
        raise RuntimeError(f"não foi possível listar os idiomas do Tesseract: {detalhe}")
    linhas = processo.stdout.splitlines()
    return {linha.strip() for linha in linhas if linha.strip() and not linha.startswith("List of")}


def verificar_dependencias(idioma: str) -> str:
    executavel = executavel_tesseract()
    if not executavel:
        raise RuntimeError(
            "Tesseract não encontrado no PATH. Instale o Tesseract e o idioma português."
        )
    idiomas = idiomas_tesseract(executavel)
    solicitados = set(idioma.split("+"))
    ausentes = sorted(solicitados - idiomas)
    if ausentes:
        raise RuntimeError(
            "idioma(s) do Tesseract ausente(s): " + ", ".join(ausentes)
        )
    return executavel


def limpar_erro(texto: str, limite: int = 240) -> str:
    texto = " ".join(texto.split()) or "Tesseract não produziu texto"
    return texto[:limite]


def executar_ocr(
    pagina: fitz.Page,
    executavel: str,
    idioma: str,
    dpi: int,
    temporario: Path,
) -> tuple[str | None, str | None]:
    imagem = temporario / f"pagina-{pagina.number + 1}.png"
    escala = dpi / 72
    pixmap = pagina.get_pixmap(
        matrix=fitz.Matrix(escala, escala),
        colorspace=fitz.csGRAY,
        alpha=False,
    )
    pixmap.save(imagem)
    processo = subprocess.run(
        [executavel, str(imagem), "stdout", "-l", idioma],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    texto = processo.stdout.strip()
    if processo.returncode != 0:
        return None, limpar_erro(processo.stderr or processo.stdout)
    if not texto:
        return None, limpar_erro(processo.stderr)
    return texto, None


def bloco_pagina(numero: int, fonte: str, texto: str) -> str:
    cabecalho = f"<!-- página {numero} | fonte: {fonte} -->"
    return f"{cabecalho}\n\n{texto.strip()}".rstrip()


@contextmanager
def pasta_temporaria(pasta_pai: Path):
    """Cria scratch local sem o chmod restritivo de tempfile no Windows."""
    caminho = pasta_pai / f".extrator-pdf-{uuid4().hex}"
    caminho.mkdir()
    try:
        yield caminho
    finally:
        shutil.rmtree(caminho, ignore_errors=True)


def extrair(pdf: Path, destino: Path, executavel: str, idioma: str, dpi: int) -> Resultado:
    resultado = Resultado(origem=pdf, destino=destino)
    blocos: list[str] = []
    destino.parent.mkdir(parents=True, exist_ok=True)
    with fitz.open(pdf) as documento, pasta_temporaria(destino.parent) as temporario:
        for indice, pagina in enumerate(documento):
            numero = indice + 1
            texto_nativo = pagina.get_text("text").strip()
            if len(texto_nativo) >= LIMIAR_CARACTERES:
                resultado.nativas += 1
                blocos.append(bloco_pagina(numero, "texto nativo", texto_nativo))
                continue

            texto_ocr, erro = executar_ocr(pagina, executavel, idioma, dpi, temporario)
            if texto_ocr is not None:
                resultado.ocr += 1
                blocos.append(bloco_pagina(numero, "Tesseract", texto_ocr))
                continue

            resultado.pendentes += 1
            preservado = texto_nativo
            marcador = f"[OCR PENDENTE: Tesseract falhou — {erro}]"
            conteudo = f"{preservado}\n\n{marcador}" if preservado else marcador
            blocos.append(bloco_pagina(numero, "pendente", conteudo))
            print(f"PENDENTE {pdf}: página {numero}: {erro}", file=sys.stderr)

    conteudo_final = SEPARADOR.join(blocos) + ("\n" if blocos else "")
    arquivo_temporario = destino.with_suffix(destino.suffix + ".tmp")
    arquivo_temporario.write_text(conteudo_final, encoding="utf-8")
    arquivo_temporario.replace(destino)
    return resultado


def selecionar_pdfs(caminhos: list[Path]) -> tuple[list[Path], bool]:
    explicitos = bool(caminhos)
    selecionados = caminhos if explicitos else sorted(Path("input").glob("*.pdf"))
    invalidos = [str(p) for p in selecionados if not p.is_file() or p.suffix.lower() != ".pdf"]
    if invalidos:
        raise RuntimeError("PDF(s) inválido(s): " + ", ".join(invalidos))
    return selecionados, explicitos


def main() -> int:
    args = argumentos()
    try:
        executavel = verificar_dependencias(args.lang)
    except RuntimeError as exc:
        print(f"ERRO DE DEPENDÊNCIA: {exc}", file=sys.stderr)
        return 2

    if args.check_deps:
        print(f"Dependências disponíveis: PyMuPDF {fitz.VersionBind}; Tesseract {executavel}; idioma {args.lang}.")
        return 0

    try:
        pdfs, explicitos = selecionar_pdfs(args.pdfs)
    except RuntimeError as exc:
        print(f"ERRO: {exc}", file=sys.stderr)
        return 2

    processados: list[Resultado] = []
    ignorados: list[Path] = []
    falhas = 0
    for pdf in pdfs:
        destino = args.output_dir / f"{pdf.stem}.md"
        if destino.exists() and not (args.force or explicitos):
            ignorados.append(pdf)
            continue
        try:
            processados.append(extrair(pdf, destino, executavel, args.lang, args.dpi))
        except Exception as exc:  # mantém os demais PDFs do lote processáveis
            falhas += 1
            print(f"FALHA {pdf}: {exc}", file=sys.stderr)

    for item in processados:
        print(
            f"GERADO {item.destino} | nativas={item.nativas} "
            f"tesseract={item.ocr} pendentes={item.pendentes}"
        )
    print(
        f"RESUMO processados={len(processados)} "
        f"ignorados={len(ignorados)} falhas={falhas}"
    )
    return 1 if falhas or any(item.pendentes for item in processados) else 0


if __name__ == "__main__":
    raise SystemExit(main())
