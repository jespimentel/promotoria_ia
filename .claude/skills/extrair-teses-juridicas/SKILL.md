---
name: extrair-teses-juridicas
description: Extrai teses jurídicas reaproveitáveis de peças processuais já convertidas em Markdown na pasta md, sanitiza os dados do caso concreto e gera notas Obsidian com YAML, tags e wikilinks. Use para processar uma peça ou PDFs em lote e formar um banco de teses.
---

# Extração de teses jurídicas

## Objetivo

Para cada peça processual, identificar argumentos, fundamentos ou raciocínios jurídicos
autônomos e reaproveitáveis e convertê-los em notas Obsidian sanitizadas. Cada origem gera um
artefato próprio:

```text
md/<base>.md → output/<base>-teses.md
```

Antes de analisar qualquer peça, leia integralmente
[`references/formato-notas.md`](references/formato-notas.md). Esse arquivo contém os critérios de
seleção e deduplicação, as regras de sanitização e o contrato obrigatório de saída.

## Entrada e extração

Esta skill analisa somente o texto já extraído em `md/`; nunca leia o PDF diretamente para
identificar teses.

- Se o usuário indicar PDF(s), localize cada `md/<base>.md`. Quando faltar, execute primeiro a
  skill `extrator-pdf` para a origem correspondente.
- Se o usuário pedir o lote sem indicar arquivos, considere todos os `input/*.pdf`, em ordem
  alfabética. Execute a `extrator-pdf` para produzir os Markdown ausentes e então processe os
  `md/<base>.md` correspondentes.
- Se o usuário indicar diretamente um ou mais `md/*.md`, processe esses arquivos.
- Não inclua automaticamente Markdown sem PDF correspondente no modo lote de PDFs.
- Trate cada origem como unidade independente. Nunca misture teses ou metadados de origens
  diferentes no mesmo artefato.

Se houver `OCR PENDENTE`, texto vazio, corrupção relevante ou ilegibilidade que impeça uma
análise confiável, não gere teses daquela origem. Registre a falha no relatório final e prossiga
com as demais. A eventual correção de OCR continua sujeita às regras da skill `extrator-pdf`.

## Seleção do lote e idempotência

1. Resolva a lista de `md/<base>.md` conforme a entrada solicitada.
2. No modo lote, pule a origem quando `output/<base>-teses.md` já existir.
3. Arquivo apontado explicitamente pelo usuário autoriza sobrescrever somente sua própria saída.
4. `--force` ou reprocessamento do lote inteiro só é permitido mediante pedido explícito.

Não use a existência de outro artefato de `output/` como sinal de processamento: a verificação é
sempre contra `output/<base>-teses.md`.

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
6. Grave todas as notas daquela origem, em sequência e sem comentários intermediários, em
   `output/<base>-teses.md`.

Se a origem não contiver tese reaproveitável, o artefato deve conter somente:

```text
Nenhuma tese reaproveitável identificada no texto fornecido.
```

## Limites de fidelidade

- Não pesquise nem complete jurisprudência, legislação ou metadados ausentes. O conteúdo deve
  ser inteiramente rastreável à origem.
- Não corrija número, tribunal, relator ou data de precedente com base em memória. Preserve o que
  a peça informa; se o dado necessário ao wikilink não estiver identificável, não o invente.
- Sem acesso explícito ao vault do usuário, deixe `relacionadas: []` e não presuma notas já
  existentes. O grafo emerge das tags e dos wikilinks compartilhados.
- Não exponha dados processuais no relatório operacional final.

## Relatório final

Depois de terminar o lote, informe de forma concisa:

- quantas origens foram processadas;
- quantas foram ignoradas por já terem saída;
- quantas falharam ou estavam ilegíveis;
- os caminhos dos artefatos gerados;
- por origem com falha, apenas o nome do arquivo e o motivo técnico, sem reproduzir conteúdo.
