---
name: extrator-pdf
description: Extrai, página por página, o texto de PDFs de input/ para Markdown em md/, usando texto nativo quando houver ao menos 400 caracteres e Tesseract OCR nas páginas abaixo desse limiar. Use ao converter, transcrever, ler ou fazer OCR de PDFs.
---

# Extração de PDF para Markdown

Converta cada PDF em um Markdown fiel, mantendo a ordem e a separação das páginas. O fluxo
normal é `input/<base>.pdf` → `md/<base>.md`.

## Execução

Na raiz do projeto, execute:

```powershell
uv run python .claude/skills/extrator-pdf/scripts/extrair_pdf.py
```

Sem argumentos, o script processa todos os `input/*.pdf` sem Markdown correspondente. Para
arquivos apontados explicitamente pelo usuário, passe os caminhos ao script; isso autoriza o
reprocessamento do Markdown correspondente. Use `--force` somente se o usuário pedir para
reprocessar todo o lote.

O script aplica obrigatoriamente a decisão a cada página, de forma independente:

1. Extrai o texto nativo com PyMuPDF.
2. Se o texto, após remover espaços nas extremidades, tiver **400 caracteres ou mais**, grava
   esse texto.
3. Se tiver **menos de 400 caracteres**, renderiza apenas essa página e executa Tesseract.
   O texto do Tesseract substitui o texto nativo curto quando o OCR produz conteúdo.
4. Se o Tesseract terminar com erro ou não produzir texto, preserva o texto nativo que existir
   e insere na página um marcador `OCR PENDENTE`.

Não classifique o documento inteiro como nativo ou digitalizado: a decisão é sempre por página.
Não resuma, corrija, complete ou interprete o conteúdo extraído.

## Dependências

Use apenas o ambiente do projeto via `uv`. O script requer PyMuPDF, já declarado no
`pyproject.toml`, e o executável `tesseract` no `PATH`.

Antes da primeira extração, verifique:

```powershell
uv run python .claude/skills/extrator-pdf/scripts/extrair_pdf.py --check-deps
```

Se o Tesseract não estiver instalado, instale-o com o gerenciador de pacotes do sistema e inclua
o idioma português. No Windows, prefira `winget install UB-Mannheim.TesseractOCR`; depois confirme
com `tesseract --version` e `tesseract --list-langs`. Instalar software do sistema pode exigir a
aprovação operacional normal do ambiente. Se `por` não estiver disponível, instale o pacote de
idioma antes de processar; não troque silenciosamente para outro idioma.

## Falha de OCR e LLM externa

O Tesseract é a única segunda tentativa automática. **Nunca envie uma página, seu texto ou seus
metadados a uma LLM externa sem autorização expressa do usuário dada depois da falha.** A
autorização genérica para extrair os PDFs ou instalar o Tesseract não autoriza esse envio.

Quando houver páginas marcadas `OCR PENDENTE`:

1. Termine as demais páginas e informe, por arquivo, os números das páginas que falharam e a
   mensagem de erro, sem expor o conteúdo do processo no relato.
2. Peça autorização explícita para enviar **somente essas páginas** a uma LLM externa, deixando
   claro que elas podem conter dados processuais sigilosos.
3. Pare e aguarde a resposta. Não presuma consentimento e não peça autorização preventiva antes
   de existir uma falha real.
4. Se autorizado, use a capacidade de visão disponível apenas nas páginas listadas, transcreva
   literalmente, substitua o marcador no Markdown e identifique essas páginas no relatório final
   como `LLM externa`.
5. Se não autorizado, mantenha o marcador e declare que o Markdown ficou incompleto nessas
   páginas.

## Saída e relatório

Cada página começa com `<!-- página N | fonte: texto nativo|Tesseract|pendente -->` e é separada
por uma linha horizontal. Preserve esse marcador para rastreabilidade; ao usar LLM autorizada,
altere a fonte da página para `LLM externa`.

Ao final, informe quantos PDFs foram processados e ignorados, os Markdown gerados e, por arquivo,
quantas páginas vieram de texto nativo, Tesseract, LLM externa ou permaneceram pendentes.

