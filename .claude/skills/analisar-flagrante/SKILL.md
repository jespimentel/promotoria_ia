---
name: analisar-flagrante
description: Analisa autos de prisão em flagrante delito a partir do texto extraído (md/<base>.md) e gera um relatório individual por auto em output/<base>-flagrante.md (sufixo próprio, para conviver com o relatório do esquematizar-processos no mesmo output/). Use quando o usuário pedir para analisar, processar ou gerar relatório dos autos de flagrante carregados.
---

# Análise de Autos de Prisão em Flagrante

## Objetivo

Você atua como assistente jurídico. Para cada auto informado (ou todos os `md/*.md` que ainda
não possuam relatório `output/<base>-flagrante.md`), produza um relatório estruturado em arquivo
`.md`, seguindo o gabarito `templates/relatorio-flagrante.md`.

Esta skill consome o **texto já extraído** em `md/<base>.md` (produzido pelo agente
`extrator-pdf`), nunca o PDF direto. Se o `md/<base>.md` de um auto ainda não existir, rode
antes o `extrator-pdf` sobre o PDF correspondente em `input/`.

## Convenção de nomes de arquivo

- O nome-base de cada auto corresponde ao número do processo/flagrante (padrão CNJ, ex.:
  `1502524-61.2024.8.26.0599`).
- O relatório de saída usa o nome-base da origem **acrescido do sufixo `-flagrante`**, com
  extensão `.md` (ex.: `md/1502524-61.2024.8.26.0599.md` →
  `output/1502524-61.2024.8.26.0599-flagrante.md`), de forma que cada auto tenha sempre seu único
  relatório correspondente em `output/` sem colidir com o relatório do `esquematizar-processos`
  (que ocupa `output/<base>.md`).
- Ainda assim, extraia o número do flagrante de dentro do conteúdo do auto (não apenas do nome
  do arquivo) e confirme se ele corresponde ao nome-base; se houver divergência, registre isso
  no relatório (no campo de observação preliminar do template).

## Passos

1. Determine a lista de autos a processar:
   - Se o usuário apontou arquivo(s) específico(s), use-os.
   - Caso contrário, liste todos os `md/*.md` cujo **`output/<base>-flagrante.md` ainda não
     exista** (a menos que o usuário peça reprocessamento). A idempotência é aferida contra o
     sufixo `-flagrante` — não contra `output/<base>.md`.
2. Para cada auto, leia o conteúdo completo de `md/<base>.md` antes de extrair qualquer
   informação.
3. Extraia, para CADA indiciado presente no auto, os seguintes campos:
   - **Número do flagrante** (padrão CNJ, ex.: 1502524-61.2024.8.26.0599)
   - **Nome do indiciado**
   - **Resumo da ocorrência** (até 2 parágrafos, texto corrido, com data, horário, local e demais circunstâncias relevantes)
   - **Prova material**
   - **Reclamação sobre tratamento policial** (sim/não, e detalhes se houver)
   - **Lesão corporal no indiciado** (sim/não, e detalhes se houver)
   - **Antecedentes criminais** (sim/não, e detalhes se houver)
4. Para cada item extraído, indique o número da(s) folha(s) (fls.) de onde a informação foi retirada — ex.: `12` ou `8-9`.
5. Leia `templates/relatorio-flagrante.md` e preencha-o com os dados extraídos, substituindo
   cada placeholder por texto corrido. Se houver mais de um indiciado no mesmo auto, repita a
   seção `## INDICIADO N: NOME COMPLETO` para cada um.
6. Use linguagem jurídica formal e precisa. Não emita opiniões pessoais nem juízos de valor.
   Se uma informação não constar dos autos, registre explicitamente "Não consta dos autos".
7. Salve o relatório preenchido em `output/<nome-base>-flagrante.md` (nome-base da origem +
   sufixo `-flagrante`).
8. Ao final, informe ao usuário, em texto, quantos autos foram processados, quantos foram ignorados (já tinham relatório) e os nomes dos relatórios gerados.

## Importante

- Cada auto gera SEMPRE um relatório individual, no nome-base da origem com o sufixo `-flagrante` — nunca consolide múltiplos autos em um único `.md`.
- Se houver mais de um indiciado no mesmo auto, todos devem constar do mesmo relatório, em seções separadas.
- Sempre referencie o número das folhas dos autos para cada informação extraída.
