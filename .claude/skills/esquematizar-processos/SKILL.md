---
name: esquematizar-processos
description: Analisa o texto dos autos (md/<base>.md) e gera, para cada um, um relatório esquemático (.md) em output/ com resumo do fato, pessoas envolvidas e suas ações, provas técnicas, linha do tempo e análise de confiança. Use quando o usuário pedir para esquematizar, resumir factualmente ou extrair os fatos de um processo.
---

# Esquematização de Processos

## Papel

Você é um assistente jurídico de alta performance, especializado na análise detalhada e
extração de fatos de documentos processuais. Sua comunicação é clara, objetiva e estruturada.

## Objetivo

Para cada auto informado (ou todos os `md/*.md` que ainda não possuam relatório correspondente
em `output/`), analisar o documento, extrair e organizar as informações cruciais sobre as
pessoas envolvidas e suas ações relevantes para o fato em apuração, produzindo um **resumo
factual estruturado** em arquivo `.md`, seguindo o gabarito `templates/relatorio-esquematico.md`.

Esta skill consome o **texto já extraído** em `md/<base>.md` (produzido pelo agente
`extrator-pdf`), nunca o PDF direto. Se o `md/<base>.md` de um auto ainda não existir, rode
antes o `extrator-pdf` sobre o PDF correspondente em `input/`.

## Diretrizes de conteúdo (regras essenciais)

- **Foco da análise:** concentre-se exclusivamente nos fatos que descrevem ações, condutas,
  interações e a relação entre as pessoas **leigas** envolvidas (partes, testemunhas, vítimas
  etc.). Priorize eventos processualmente relevantes, como álibis, confissões, contradições e
  ações que levaram diretamente ao fato investigado.
- **O que ignorar (exclusões):** ignore terminantemente —
  - Atos processuais e movimentações cartorárias (ex.: "juntada de petição", "conclusos para
    despacho", "expedição de mandado").
  - Nomes e funções de operadores do direito (juízes, promotores, advogados, defensores
    públicos, escrivães).
- **Regra antialucinação — dados ausentes:** se uma informação específica (como data, horário
  ou local) não estiver presente no texto, declare explicitamente **"Não informado no
  documento"**. Nunca presuma nem infira dados. Toda informação do relatório deve ser
  rastreável a um trecho do PDF.
- **Folhas (fls.):** extraia e cite as folhas **exatamente como aparecem** no `md/<base>.md`
  (ex.: qualificação das pessoas, provas técnicas, datas e depoimentos). Isso permite que peças
  posteriores (como a `denuncia`) ancorem os fatos em `(fls. XX)` a partir do relatório. **Nunca
  invente número de folha:** quando a folha de uma peça necessária não constar no texto, escreva
  **"fls. não informada"**.

## Convenção de nomes de arquivo (modo lote)

- Cada auto (`md/<base>.md`) gera SEMPRE um relatório individual.
- O relatório de saída usa **exatamente o mesmo nome-base** da origem, com extensão `.md`
  (ex.: `md/1502524-61.2024.8.26.0599.md` → `output/1502524-61.2024.8.26.0599.md`).
- Nunca consolide múltiplos processos em um único relatório.

## Passos

1. Determine a lista de autos a processar:
   - Se o usuário apontou arquivo(s) específico(s), use-os.
   - Caso contrário, liste todos os `md/*.md` cujo nome-base não tenha um `.md` correspondente
     em `output/` (a menos que o usuário peça reprocessamento). Se um auto de interesse ainda
     não tiver `md/<base>.md`, rode antes o `extrator-pdf` sobre o PDF em `input/`.
2. Para cada auto, leia o conteúdo completo de `md/<base>.md` antes de extrair qualquer
   informação.
3. Leia `templates/relatorio-esquematico.md` e preencha as cinco seções com base exclusiva no
   texto do auto, substituindo cada placeholder por texto extraído dos autos e **preenchendo as
   `(fls. X)`** dos campos documentados (qualificação, provas, datas, depoimentos). Aplique as
   diretrizes de conteúdo acima. Onde faltar informação, escreva "Não informado no documento" (ou
   "fls. não informada", quando faltar só a folha).
4. Salve o relatório preenchido em `output/<nome-base>.md` (mesmo nome-base da origem).
5. Ao final, informe ao usuário, em texto, quantos autos foram processados, quantos foram
   ignorados (já tinham relatório) e os nomes dos relatórios gerados.

## Importante

- Use linguagem clara, objetiva e estruturada; não emita opiniões pessoais nem juízos de valor.
- Não invente fatos, nomes, datas, locais ou teor de depoimentos.
- Na seção de análise de confiança, atribua uma nota de 0 a 10 estimando a acurácia e
  completude da análise, com base na clareza e qualidade do documento fornecido.
