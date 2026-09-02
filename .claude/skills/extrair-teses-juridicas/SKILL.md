---
name: extrair-teses-juridicas
description: Extrai teses jurídicas reaproveitáveis de peças processuais já convertidas em Markdown na pasta md, sanitiza os dados do caso concreto e grava, para cada uma, um bloco de staging em output/<base>-teses.md e uma nota Obsidian solta (frontmatter YAML, tags e wikilinks) em output/teses/<arquivo>.md, formando um banco de teses navegável. Use para processar uma peça, PDFs ou .docx em lote.
---

# Extração de teses jurídicas

## Objetivo

Para cada peça processual, identificar argumentos, fundamentos ou raciocínios jurídicos
autônomos e reaproveitáveis e convertê-los em notas Obsidian sanitizadas. Cada origem gera dois
artefatos:

```text
md/<base>.md → output/<base>-teses.md            (staging, um bloco cercado por tese)
             → output/teses/<arquivo-da-tese>.md  (nota final, uma por tese, sem cerca)
```

`output/<base>-teses.md` é o artefato de staging por origem, útil para revisão e para o relatório
de idempotência. `output/teses/` é o banco de teses em si: cada nota é gravada solta, com
frontmatter YAML real (sem cerca de código), para que o Obsidian reconheça wikilinks e a nota
entre no grafo. Sem essa gravação solta, os wikilinks e o frontmatter ficam inertes dentro do
bloco cercado do staging e nenhum cruzamento acontece.

Antes de analisar qualquer peça, leia integralmente
[`references/formato-notas.md`](references/formato-notas.md). Esse arquivo contém os critérios de
seleção e deduplicação, as regras de sanitização e o contrato obrigatório de saída.

## Entrada e extração

Esta skill analisa somente o texto já extraído em `md/`; nunca leia o PDF diretamente para
identificar teses.

- Se o usuário indicar PDF(s), localize cada `md/<base>.md`. Quando faltar, execute primeiro a
  skill `extrator-pdf` para a origem correspondente.
- Se o usuário indicar `.docx`, localize cada `md/<base>.md`. Quando faltar, execute primeiro
  `.claude/skills/resumidor-pecas/scripts/extrair_texto.py` (`uv run python`) para a origem
  correspondente.
- Se o usuário pedir o lote de PDFs sem indicar arquivos, considere todos os `input/*.pdf`, em
  ordem alfabética. Execute a `extrator-pdf` para produzir os Markdown ausentes e então processe
  os `md/<base>.md` correspondentes.
- Se o usuário pedir o lote de `.docx` sem indicar arquivos, considere todos os `input/*.docx`,
  em ordem alfabética. Execute `extrair_texto.py` para produzir os Markdown ausentes e então
  processe os `md/<base>.md` correspondentes.
- Se o usuário indicar diretamente um ou mais `md/*.md`, processe esses arquivos.
- Não inclua automaticamente Markdown sem origem (PDF ou `.docx`) correspondente no modo lote.
- Trate cada origem como unidade independente. Nunca misture teses ou metadados de origens
  diferentes no mesmo artefato.

Se houver `OCR PENDENTE`, texto vazio, corrupção relevante ou ilegibilidade que impeça uma
análise confiável, não gere teses daquela origem. Registre a falha no relatório final e prossiga
com as demais. A eventual correção de OCR continua sujeita às regras da skill `extrator-pdf`.

## Seleção do lote e idempotência

1. Resolva a lista de `md/<base>.md` conforme a entrada solicitada.
2. No modo lote, pule a origem quando `output/<base>-teses.md` já existir (idempotência por
   origem, igual às demais skills do projeto).
3. Arquivo apontado explicitamente pelo usuário autoriza sobrescrever sua própria saída de
   staging (`output/<base>-teses.md`) e regravar as notas dessa origem em `output/teses/`.
4. `--force` ou reprocessamento do lote inteiro só é permitido mediante pedido explícito.

Não use a existência de outro artefato de `output/` como sinal de processamento: a verificação é
sempre contra `output/<base>-teses.md`.

Dentro de uma mesma origem, antes de gravar cada nota em `output/teses/<arquivo>.md`, verifique
se esse caminho já existe:

- Se já existir e o conteúdo (frontmatter e corpo) for equivalente, não regrave; conte a tese
  como já presente no banco e cite o caminho existente no relatório.
- Se já existir com conteúdo divergente, não sobrescreva silenciosamente: acrescente um sufixo
  numérico ao slug (`-2`, `-3`, ...) para a nova nota e registre a colisão no relatório final,
  para revisão manual — teses de fundamentos distintos não podem se sobrepor no banco.

## Processamento de cada origem

1. Leia integralmente o Markdown e desconsidere apenas os marcadores técnicos de página da
   extração, cabeçalhos, rodapés, numeração e marcas d'água repetidos.
2. Identifique se há uma ou várias peças e determine, a partir do texto, o tipo de origem de cada
   tese e o número CNJ do processo, quando identificável.
3. Separe as teses pelo fundamento jurídico central. Aplique os critérios de seleção e
   deduplicação do contrato; não extraia simples narrativa factual, pedido, ementa ou citação
   isolada.
4. Sanitize cada tese sem empobrecer o raciocínio jurídico. Preserve integralmente dispositivos
   legais e citações jurisprudenciais efetivamente presentes.
5. Monte cada nota conforme o contrato. Faça uma revisão final específica para detectar nomes,
   números de processo, datas, locais, valores e referências aos autos fora do campo
   `processo_origem`.
6. Grave todas as notas daquela origem, em sequência e sem comentários intermediários, no
   staging `output/<base>-teses.md` (cada uma em seu bloco cercado, conforme o contrato).
7. Para cada tese do lote de staging, grave também a nota final solta, sem cerca de código, em
   `output/teses/<arquivo>.md` — mesmo frontmatter e corpo do bloco, sem os delimitadores
   ```` ```markdown ```` / ```` ``` ````. Aplique a regra de deduplicação por slug acima.

Se a origem não contiver tese reaproveitável, o staging `output/<base>-teses.md` deve conter
somente:

```text
Nenhuma tese reaproveitável identificada no texto fornecido.
```

Nesse caso, não crie nenhum arquivo em `output/teses/`.

## Limites de fidelidade

- Não pesquise nem complete jurisprudência, legislação ou metadados ausentes. O conteúdo deve
  ser inteiramente rastreável à origem.
- Não corrija número, tribunal, relator ou data de precedente com base em memória. Preserve o que
  a peça informa; se o dado necessário ao wikilink não estiver identificável, não o invente.
- Sem acesso explícito ao vault do usuário, deixe `relacionadas: []` e não presuma notas já
  existentes. O grafo emerge das tags e dos wikilinks de jurisprudência/legislação
  compartilhados entre as notas soltas em `output/teses/` — reaproveite o mesmo texto de
  wikilink (grafia e formatação) sempre que a origem citar o mesmo precedente ou dispositivo já
  usado em outra tese do banco, para que o cruzamento realmente ocorra.
- Não exponha dados processuais no relatório operacional final.

## Relatório final

Depois de terminar o lote, informe de forma concisa:

- quantas origens foram processadas;
- quantas foram ignoradas por já terem saída;
- quantas falharam ou estavam ilegíveis;
- quantas teses novas foram gravadas em `output/teses/`, quantas já existiam (deduplicadas) e
  quantas colidiram com slug divergente (sufixo numérico, para revisão manual);
- os caminhos dos artefatos gerados, tanto do staging (`output/<base>-teses.md`) quanto das notas
  finais (`output/teses/<arquivo>.md`);
- por origem com falha, apenas o nome do arquivo e o motivo técnico, sem reproduzir conteúdo.
