# Projeto: Promotoria IA — Biblioteca de Skills

Repositório que reúne **skills** de apoio ao trabalho na promotoria. Cada skill automatiza
uma tarefa jurídica específica (análise de autos, redação de peças etc.) e é acionada a
partir da **raiz** do repositório.

## Pipeline de pastas (compartilhado por todas as skills)

Todo o trabalho segue um **pipeline de três estágios** com pastas **planas e compartilhadas**
na raiz do repositório:

```
input/   (PDFs, .docx e mídias)  →  [extração]  →  md/  (texto em Markdown)  →  [skills]  →  output/ (.md)
```

- **`input/`** — documentos e mídias de origem (PDF, `.docx`, áudio e vídeo), sem subpastas.
- **`md/`** — o conteúdo extraído em Markdown, com nome-base espelhado para documentos
  (`123.pdf` → `md/123.md`; `peca.docx` → `md/peca.md`) e sufixo próprio para transcrições
  (`123.mp4` → `md/123-transcricao.md`). O conteúdo é extraído **uma única vez**.
- **`output/`** — os artefatos gerados pelas skills, sempre em `.md`, também com nome-base
  espelhado (`md/123.md` → `output/123.md`).

**Estágio de extração** (produz o `md/`):

- **PDFs** → skill `extrator-pdf` (`.claude/skills/extrator-pdf/`), que avalia cada página e
  usa Tesseract quando houver menos de 400 caracteres de texto nativo.
- **`.docx`** → script `extrair_texto.py` (da `resumidor-pecas`), que grava direto em `md/`.
- **Áudio e vídeo** → skill `transcrever-midia` (`.claude/skills/transcrever-midia/`), que extrai
  o áudio com FFmpeg e transcreve localmente com faster-whisper em
  `md/<base>-transcricao.md`, sem colidir com o Markdown do PDF.

**As skills nunca leem o PDF/`.docx` direto: consomem sempre o `md/<base>.md`.** Se o MD ainda
não existir, rode antes o estágio de extração.

## Skills disponíveis

Todas leem o texto em `md/<base>.md`. Quanto à **saída** no `output/` plano, no fluxo dos **autos**
(nome-base = número CNJ do processo) vale a regra (ver "Restrição do `output/` plano"):

- **`esquematizar-processos`** grava no **nome-base puro** `output/<base>.md` — é o relatório
  canônico dos autos, consumido pela `denuncia`.
- **`analisar-flagrante`, `alegacoes-finais`, `denuncia`** gravam com **sufixo próprio**
  `output/<base>-<nome-da-skill>.md` (`-flagrante`, `-alegacoes-finais`, `-denuncia`), convivendo
  com aquele relatório no mesmo nome-base.
- **`resumidor-pecas`** é um **fluxo à parte** (triagem de peças avulsas, nome-base = nome da peça,
  não o número do processo): grava `output/<peça>.md` + um `indice.md` consolidado; não colide com
  o fluxo dos autos.

- **`extrator-pdf`** (`.claude/skills/extrator-pdf/`) — extrai cada PDF de `input/` para
  `md/`, página por página, usando Tesseract nas páginas com menos de 400 caracteres.
- **`transcrever-midia`** (`.claude/skills/transcrever-midia/`) — transcreve localmente arquivos
  de áudio e vídeo de `input/` para `md/<base>-transcricao.md`, com timestamps e metadados de
  associação, usando FFmpeg e faster-whisper.
- **`alegacoes-finais`** (`.claude/skills/alegacoes-finais/`) — redige minuta de alegações
  finais em ação penal analisando conjuntamente `md/<base>.md` e todas as
  `md/*-transcricao.md` associadas ao processo pelo CNJ. Uma transcrição nunca é tratada como auto
  independente. Grava `output/<base>-alegacoes-finais.md`.
- **`analisar-flagrante`** (`.claude/skills/analisar-flagrante/`) — analisa autos de prisão
  em flagrante e gera um relatório estruturado por auto. Grava `output/<base>-flagrante.md`
  (sufixo, não o nome-base puro — ver Convenções).
- **`denuncia`** (`.claude/skills/denuncia/`) — **etapa opcional** (segunda etapa) que redige a
  denúncia criminal a partir do relatório esquemático (`output/<base>.md`, fonte primária das
  `fls.`), usando `md/<base>.md` só para conferir números e como fallback. Só roda a **pedido
  expresso**. Grava `output/<base>-denuncia.md` (sufixo, não o nome-base puro — ver Convenções).
- **`esquematizar-processos`** (`.claude/skills/esquematizar-processos/`) — esquematiza autos
  de um processo e gera um relatório esquemático `.md` (resumo do fato, pessoas e suas ações,
  provas técnicas com `fls.`, linha do tempo e análise de confiança).
- **`resumidor-pecas`** (`.claude/skills/resumidor-pecas/`) — lê peças processuais (originadas
  de `.docx` ou `.pdf`) e gera, para cada uma, um `.md` com frontmatter (arquivo de origem,
  tipo de peça e resumo em até 4 linhas) seguido do texto integral, além de um `indice.md`
  consolidado para disclosure progressivo.
- **`extrair-teses-juridicas`** (`.claude/skills/extrair-teses-juridicas/`) — identifica em peças
  processuais teses jurídicas autônomas e reaproveitáveis, sanitiza os dados do caso concreto e
  grava dois artefatos por origem: o staging `output/<base>-teses.md` (um bloco cercado por
  tese) e, para cada tese, uma nota Obsidian solta (frontmatter YAML, tags e wikilinks) em
  `output/teses/<arquivo-da-tese>.md` — é essa pasta plana que forma o banco de teses navegável
  no grafo. **Exceção deliberada** à regra de pastas planas por origem (ver Convenções): como as
  notas não são "uma por origem" mas "uma por tese", `output/teses/` reúne o banco inteiro,
  deduplicado por slug.

## Convenções

- **Skills** ficam sempre em `.claude/skills/<nome-da-skill>/`, com o `SKILL.md` e quaisquer
  assets (scripts, templates, exemplos) dentro da própria pasta da skill.
- **Assets da skill, por convenção de nome:**
  - `templates/` — formulário/gabarito com placeholders, a estrutura que a skill preenche.
  - `exemplos/` — casos **reais** completos, usados só como referência de forma/estilo
    (nunca como fonte de fatos). Por serem reais, são **sigilosos** e não vão para o GitHub.
- **Pastas do pipeline são compartilhadas** (`input/`, `md/`, `output/`, planas — ver seção
  "Pipeline de pastas"). **Não** crie subpastas por skill. Exceção deliberada:
  `output/teses/` (`extrair-teses-juridicas`), que não indexa por origem, mas por tese — ver a
  entrada da skill acima.
- Ao adicionar uma skill nova, repita o padrão: pasta em `.claude/skills/`; ela consome
  `md/<base>.md` e grava em `output/`. **Escolha o nome de saída para não colidir:** no fluxo dos
  autos, `output/<base>.md` é reservado ao relatório canônico do `esquematizar-processos`; qualquer
  outra skill desse fluxo grava com **sufixo próprio** `output/<base>-<nome-da-skill>.md`.

### Processamento em lote e idempotência (padrão obrigatório)

O pipeline tem **dois estágios idempotentes**. Este é o padrão do projeto e vale também para
as skills futuras:

- **Estágio de extração (input → md):** PDFs e `.docx` produzem `md/<base>.md`; mídias produzem
  `md/<base>-transcricao.md`. **Pula** origens cuja saída correspondente já exista.
- **Estágio de skill (md → output):** a skill consome sempre o `md/<base>.md` (nunca o
  PDF/`.docx` direto). Se o usuário não apontar arquivo(s) específico(s), processa **todos** os
  `md/*.md`, gerando **um artefato por origem** (nunca consolide vários processos num só
  artefato). **Pula** os que já tiverem a **sua própria** saída — cada skill afere a idempotência
  contra o nome que ela mesma grava: `output/<base>.md` para o `esquematizar-processos`;
  `output/<base>-<nome-da-skill>.md` para as demais skills do fluxo dos autos.
- **Transcrições não são autos:** arquivos `md/*-transcricao.md` ou com
  `tipo_documento: transcricao_midia` são fontes complementares. Não entram no lote como processos
  independentes; `alegacoes-finais` associa-os pelo CNJ e os analisa com o auto correspondente.
- **Nome-base espelhado em toda a cadeia:** `123.pdf` → `md/123.md` → `output/123.md`
  (`esquematizar-processos`) ou `output/123-<skill>.md` (demais). É isso que torna a
  correspondência origem↔extração↔saída inequívoca. Mídias são a exceção deliberada na extração:
  usam `md/<base>-transcricao.md` para coexistir com o auto.
- **Restrição do `output/` plano (importante):** como `output/` é plano e todas as skills geram
  `.md`, o espaço de nomes é único. Para evitar colisão no fluxo dos autos, **apenas o
  `esquematizar-processos` grava no nome-base puro** `output/<base>.md` (relatório canônico); todas
  as demais skills desse fluxo (`analisar-flagrante`, `alegacoes-finais`, `denuncia`) gravam com
  **sufixo próprio** `output/<base>-<nome-da-skill>.md`. Assim, o relatório e os demais artefatos
  coexistem no mesmo nome-base, e a `denuncia` pode inclusive **consumir** o relatório sem
  sobrescrevê-lo. (O `resumidor-pecas` está em outro universo de nomes — peças avulsas — e não
  entra nessa disputa.) Para **refazer** um artefato já existente, **aponte o arquivo
  explicitamente** (a skill sobrescreve) ou peça reprocessamento.
- **Nunca trate o relatório do `esquematizar-processos` como "já processado" por outra skill:** cada
  skill afere idempotência contra o **seu próprio** nome de saída, jamais contra `output/<base>.md`
  quando este for a fonte.
- Ao final, cada estágio informa em texto quantas origens foram processadas, quantas foram
  ignoradas (já tinham saída) e os nomes dos artefatos gerados.

## Ambiente Python (uv)

O projeto usa **`uv`** para gerir o ambiente. As dependências ficam no `pyproject.toml`
(ex.: `python-docx`, usada pela `resumidor-pecas` para ler `.docx`; `pymupdf`, usada pelo
skill `extrator-pdf`).

- Adicionar dependência: `uv add <pacote>`.
- Executar scripts: `uv run python <caminho-do-script> ...` — o `uv run` cria/sincroniza o
  `.venv/` automaticamente. Nunca use o Python global nem crie `.venv` manualmente.

## Versionamento e sigilo

São **dados sigilosos** e ficam fora do GitHub (ignorados pelo `.gitignore`, exceto os
`.gitkeep` que preservam a estrutura de pastas):

- `input/`, `md/` e `output/` — autos de entrada, texto extraído e peças/relatórios gerados.
- `.claude/skills/**/exemplos/` — os casos reais usados como referência de estilo.

Nunca remova essas entradas do `.gitignore`: elas permitem compartilhar as skills via GitHub
sem expor dados de processos.
