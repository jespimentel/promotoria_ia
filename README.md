# Promotoria IA — Biblioteca de Skills

Biblioteca de **skills** ([Claude Code](https://claude.com/claude-code)) de apoio ao trabalho na
promotoria. Cada skill automatiza uma tarefa jurídica específica — analisar autos, esquematizar
processos, redigir alegações finais, minutar denúncias — a partir de um **pipeline comum** de
extração e reaproveitamento do texto dos documentos.

O objetivo é extrair o texto de cada documento **uma única vez** (com OCR quando necessário) e
reutilizá-lo em qualquer skill, economizando tokens e centralizando o reconhecimento de texto.

> ⚠️ **Sigilo processual.** As pastas de dados (`input/`, `md/`, `output/`) e os `exemplos/` reais
> das skills **não** vão para o GitHub (ver [Sigilo e versionamento](#sigilo-e-versionamento)).
> O repositório compartilha **apenas as skills** — nunca autos ou peças.

## Pipeline

Todo o trabalho segue três estágios, com pastas **planas e compartilhadas** na raiz:

```
input/                 md/                      output/
(PDFs e .docx)   →   (texto em Markdown)   →   (.md gerados)
  origem          extração (uma vez)          skills
```

- **`input/`** — documentos de origem (PDFs dos autos e `.docx` de peças), sem subpastas.
- **`md/`** — o **texto extraído** de cada origem, em Markdown, com **nome-base espelhado**
  (`123.pdf` → `md/123.md`). Extraído uma única vez e reaproveitado por qualquer skill.
- **`output/`** — os artefatos gerados pelas skills, em `.md` (ver
  [convenção de nomes](#convenção-de-nomes-de-saída)).

**As skills nunca leem o PDF/`.docx` direto — consomem sempre o `md/<base>.md`.** Se o `md/` de
uma origem ainda não existir, rode antes o estágio de extração.

### Estágio de extração (produz o `md/`)

- **PDFs** → skill [`extrator-pdf`](.claude/skills/extrator-pdf/SKILL.md), que avalia cada página
  e usa **Tesseract OCR** quando houver menos de 300 caracteres de texto nativo.
- **`.docx`** → script `extrair_texto.py` (da skill `resumidor-pecas`), que grava direto em `md/`.

## Skills disponíveis

O estágio de entrada é a skill [`extrator-pdf`](.claude/skills/extrator-pdf/): ela converte
`input/<base>.pdf` em `md/<base>.md`, página por página, recorrendo ao Tesseract abaixo do limiar
de 300 caracteres.

Todas leem `md/<base>.md`. O **fluxo dos autos** (nome-base = número CNJ do processo) reúne:

| Skill | O que faz | Saída |
|---|---|---|
| [`esquematizar-processos`](.claude/skills/esquematizar-processos/) | Extrai e organiza os fatos dos autos: resumo do fato, pessoas e ações, provas técnicas (com `fls.`), linha do tempo e análise de confiança. **Relatório canônico** consumido pela denúncia. | `output/<base>.md` |
| [`analisar-flagrante`](.claude/skills/analisar-flagrante/) | Analisa autos de prisão em flagrante e gera um relatório estruturado por auto (por indiciado). | `output/<base>-flagrante.md` |
| [`alegacoes-finais`](.claude/skills/alegacoes-finais/) | Redige minuta de alegações finais (memoriais) em ação penal. | `output/<base>-alegacoes-finais.md` |
| [`denuncia`](.claude/skills/denuncia/) | **Etapa opcional.** Redige a denúncia criminal a partir do relatório do `esquematizar-processos` (fonte primária das `fls.`). Só roda a **pedido expresso**. | `output/<base>-denuncia.md` |

Fora do fluxo dos autos:

| Skill | O que faz | Saída |
|---|---|---|
| [`resumidor-pecas`](.claude/skills/resumidor-pecas/) | Lê peças processuais avulsas e gera, para cada uma, um `.md` com frontmatter (origem, tipo, resumo) + texto integral, além de um `indice.md` consolidado para disclosure progressivo. | `output/<peça>.md` + `output/indice.md` |
| [`extrair-teses-juridicas`](.claude/skills/extrair-teses-juridicas/) | Extrai teses jurídicas autônomas e reaproveitáveis de peças, remove os dados do caso concreto e gera notas Obsidian com YAML, tags e wikilinks. | `output/<base>-teses.md` |

## Como usar

As skills são acionadas por **linguagem natural** — o Claude Code reconhece o pedido e dispara a
skill certa. Rodar **em lote** significa não apontar arquivo específico: a skill processa todos os
`md/*.md` sem saída correspondente e pula os já feitos.

Comece pela extração (se ainda houver só PDFs em `input/`):

> Extraia o texto de todos os PDFs de `input/` para `md/`.

Depois, exemplos de acionamento em lote:

> Esquematize todos os processos.
>
> Analise todos os autos de flagrante.
>
> Elabore as alegações finais de todos os processos.
>
> Extraia as teses jurídicas de todos os PDFs em lote.

A **denúncia** depende do relatório do esquematizar, então encadeie:

> Esquematize todos os processos e, em seguida, elabore a denúncia de cada um.

Para trabalhar um único auto (ou **refazer** um artefato existente), aponte o arquivo — a skill
então sobrescreve:

> Elabore as alegações finais do `md/1502524-61.2024.8.26.0599.md`.

## Convenção de nomes de saída

Como `output/` é **plano** e todas as skills geram `.md`, o espaço de nomes é único. Para as
skills do **fluxo dos autos** conviverem no mesmo nome-base sem colisão:

- **Apenas o `esquematizar-processos`** grava no nome-base puro `output/<base>.md` (o relatório
  canônico consumido pela denúncia).
- **As demais** gravam com **sufixo próprio**: `output/<base>-<nome-da-skill>.md`
  (`-flagrante`, `-alegacoes-finais`, `-denuncia`).

Assim, para um mesmo auto `<base>`, as quatro saídas coexistem:

```
output/<base>.md                     ← esquematizar-processos (relatório)
output/<base>-flagrante.md           ← analisar-flagrante
output/<base>-alegacoes-finais.md    ← alegacoes-finais
output/<base>-denuncia.md            ← denuncia
```

## Processamento em lote e idempotência

O pipeline tem **dois estágios idempotentes** (padrão obrigatório do projeto):

- **Extração (input → md):** para cada origem em `input/`, produz `md/<base>.md`; **pula** origens
  que já tenham `md/<base>.md`.
- **Skill (md → output):** processa todos os `md/*.md` sem a saída correspondente, gerando **um
  artefato por origem** (nunca consolida vários processos num só); **pula** os que já tiverem a
  **sua própria** saída. Cada skill afere a idempotência contra o nome que **ela mesma** grava —
  jamais contra `output/<base>.md` quando este for a fonte (o relatório).

Reprocessar exige pedido explícito (ou apontar o arquivo, que a skill então sobrescreve).

## Estrutura do repositório

```
.
├── input/                 # origens (PDF/.docx) — sigiloso, fora do Git
├── md/                    # texto extraído — sigiloso, fora do Git
├── output/                # artefatos gerados — sigiloso, fora do Git
├── .claude/
│   ├── agents/
│   │   └── extrator-pdf.md         # compatibilidade com chamadas antigas
│   └── skills/
│       ├── extrator-pdf/           # extração página a página + Tesseract OCR
│       ├── extrair-teses-juridicas/# teses sanitizadas em notas Obsidian
│       ├── esquematizar-processos/
│       ├── analisar-flagrante/
│       ├── alegacoes-finais/
│       ├── denuncia/
│       └── resumidor-pecas/
├── CLAUDE.md              # instruções do projeto para o Claude Code
├── pyproject.toml         # dependências (uv)
└── README.md
```

Cada skill vive em `.claude/skills/<nome>/` com seu `SKILL.md` e assets:

- **`templates/`** — gabarito com placeholders, a estrutura que a skill preenche (vai para o Git).
- **`exemplos/`** — casos **reais** usados só como referência de forma/estilo (nunca como fonte de
  fatos). Por serem reais, são **sigilosos** e ficam fora do Git.

## Ambiente Python (uv)

O projeto usa [`uv`](https://docs.astral.sh/uv/) para gerir o ambiente. As dependências estão no
`pyproject.toml` (`pymupdf`, usada pelo `extrator-pdf`; `python-docx`, usada pela
`resumidor-pecas`).

- Adicionar dependência: `uv add <pacote>`
- Executar scripts: `uv run python <caminho-do-script> ...` — o `uv run` cria/sincroniza o
  `.venv/` automaticamente. Nunca use o Python global nem crie `.venv` manualmente.

## Sigilo e versionamento

São **dados sigilosos** e ficam fora do GitHub (ignorados pelo `.gitignore`, exceto os `.gitkeep`
que preservam a estrutura de pastas):

- `input/`, `md/` e `output/` — autos de entrada, texto extraído e peças/relatórios gerados.
- `.claude/skills/**/exemplos/` — os casos reais usados como referência de estilo.

Essas entradas do `.gitignore` permitem **compartilhar as skills** via GitHub sem expor dados de
processos — não as remova.
