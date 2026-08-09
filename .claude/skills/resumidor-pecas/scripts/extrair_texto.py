"""Extrai o texto de um arquivo .docx e grava em md/<nome-base>.md.

Uso:
    uv run python .claude\\skills\\resumidor-pecas\\scripts\\extrair_texto.py <arquivo.docx> [saida.md]

É o estágio de extração do pipeline (input/ -> md/ -> output/) para arquivos .docx:
o texto vira Markdown em `md/`, com nome-base espelhado (`peca.docx` -> `md/peca.md`),
para depois ser consumido pelas skills. Se `saida.md` não for informado, o destino
padrão é `md/<nome-base>.md` na raiz do repositório. O script é idempotente por chamada:
sobrescreve o destino indicado; a decisão de pular arquivos já extraídos cabe a quem chama.

Motivo: a ferramenta de leitura do Claude lê PDF nativamente, mas não lê .docx.
Este script usa python-docx (já declarado no pyproject.toml da raiz) para converter
o conteúdo do documento — parágrafos e tabelas — em texto simples, preservando a
ordem de leitura do documento.
"""

import sys
from pathlib import Path

# Raiz do repositório: .../promotoria_ia/.claude/skills/resumidor-pecas/scripts/este_arquivo
RAIZ_REPO = Path(__file__).resolve().parents[4]

from docx import Document
from docx.document import Document as _Document
from docx.oxml.table import CT_Tbl
from docx.oxml.text.paragraph import CT_P
from docx.table import Table
from docx.text.paragraph import Paragraph


def iter_blocos(parent):
    """Percorre parágrafos e tabelas na ordem em que aparecem no documento."""
    if isinstance(parent, _Document):
        elm = parent.element.body
    else:
        elm = parent._element
    for child in elm.iterchildren():
        if isinstance(child, CT_P):
            yield Paragraph(child, parent)
        elif isinstance(child, CT_Tbl):
            yield Table(child, parent)


def extrair(caminho: Path) -> str:
    doc = Document(str(caminho))
    linhas: list[str] = []
    for bloco in iter_blocos(doc):
        if isinstance(bloco, Paragraph):
            linhas.append(bloco.text)
        elif isinstance(bloco, Table):
            for linha in bloco.rows:
                celulas = [c.text.strip() for c in linha.cells]
                linhas.append(" | ".join(celulas))
    return "\n".join(linhas)


def main() -> int:
    if len(sys.argv) not in (2, 3):
        print("Uso: extrair_texto.py <arquivo.docx> [saida.md]", file=sys.stderr)
        return 2
    caminho = Path(sys.argv[1])
    if not caminho.is_file():
        print(f"Arquivo não encontrado: {caminho}", file=sys.stderr)
        return 1

    if len(sys.argv) == 3:
        saida = Path(sys.argv[2])
    else:
        saida = RAIZ_REPO / "md" / (caminho.stem + ".md")

    saida.parent.mkdir(parents=True, exist_ok=True)
    saida.write_text(extrair(caminho), encoding="utf-8")
    print(saida)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
