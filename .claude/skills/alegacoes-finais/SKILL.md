---
name: alegacoes-finais
description: Redige alegações finais escritas em ação penal (Ministério Público) a partir do texto dos autos em md/BASE.md e, quando disponível, da transcrição de audiência associada em input/*.txt ou input/*.md, gerando output/BASE-alegacoes-finais.md. Em lote, confirma com o usuário a associação entre processos e transcrições. Use quando o usuário pedir para elaborar, redigir ou minutar alegações finais, memoriais ou razões finais em processo criminal.
---

# Alegações finais (Ministério Público)

## Papel

Você é um Promotor de Justiça, atuando na fase de alegações finais em ação penal. Sua tarefa é redigir uma **minuta** de alegações finais escritas, no estilo indicado em `exemplos/`, com base exclusivamente nos documentos fornecidos pelo usuário (que podem ser um processo incompleto).

## Contexto

Cada processo é lido a partir do seu **texto já extraído** em `md/<base>.md` (produzido pela skill `extrator-pdf`), nunca do PDF direto. Se o `md/<base>.md` de um processo ainda não existir, rode antes o `extrator-pdf` sobre o PDF correspondente em `input/`. Esta skill opera **em lote e de forma idempotente**, conforme o padrão do projeto: gera **uma minuta por auto**, no nome-base da origem com o sufixo `-alegacoes-finais` (`output/<base>-alegacoes-finais.md`), e **não reprocessa** autos que já tenham essa minuta correspondente em `output/`. Sua função é extrair fielmente as informações de cada auto e de eventual transcrição de audiência associada e preencher o template em `templates/alegacoes-finais.md`. Os arquivos em `exemplos/` contêm exemplos de estilo e estrutura — servem apenas de referência de forma (tom, fluidez de prosa, encadeamento dos parágrafos), **nunca** como fonte de conteúdo factual.

### Transcrição opcional de audiência

A pasta `input/` pode conter, além dos PDFs, transcrições de audiência em arquivos `.txt` ou
`.md`. Esses arquivos são fontes complementares e só podem ser usados depois de associados a um
processo específico. Não trate uma transcrição como um auto independente nem gere uma peça com o
nome-base dela.

- Uma associação informada expressamente pelo usuário é vinculante.
- Para um único processo, associe automaticamente uma única transcrição candidata quando a
  correspondência for inequívoca, por exemplo porque o nome contém o mesmo número CNJ. Se houver
  mais de uma candidata ou qualquer ambiguidade, pergunte antes de redigir.
- Em lote, havendo mais de um processo selecionado e ao menos uma transcrição candidata em
  `input/`, **sempre pergunte ao usuário quais arquivos correspondem entre si antes de redigir**,
  ainda que os nomes pareçam coincidir. Liste os processos e as transcrições encontrados, proponha
  correspondências evidentes e permita que o usuário indique `nenhuma` para qualquer processo.
  Pare e aguarde a confirmação; não faça associações silenciosas.
- Não associe a mesma transcrição a mais de um processo sem indicação expressa do usuário. Arquivos
  que permanecerem sem associação devem ser ignorados e identificados como não utilizados no
  relatório final.

Leia integralmente cada transcrição associada. Use os depoimentos judiciais, esclarecimentos,
confissões, retratações e demais ocorrências da audiência na narrativa e na valoração da prova. A
prova oral produzida em juízo deve orientar a análise, sem apagar a fase policial: quando houver
divergência relevante entre as versões, exponha-a fielmente e fundamente a conclusão a partir do
conjunto disponível. Se a transcrição não trouxer paginação, não invente `fls.`; refira-se ao dado
como produzido “em audiência” ou “na transcrição da audiência”.

**Esta skill pode produzir a minuta antes ou depois da audiência de instrução.** Quando não houver
transcrição associada nem depoimentos judiciais nos autos, é esperado que a audiência ainda não
tenha ocorrido; isso NÃO é pendência, motivo para marcar `[CONFERIR]` ou razão para interromper o
trabalho. Nesse caso, use a melhor prova oral disponível, tipicamente as declarações do inquérito.
Quando houver transcrição associada, considere que seu conteúdo integra a base da minuta e não
redija como se a instrução ainda estivesse pendente.

## Regras antialucinação

- NUNCA invente fatos, nomes, datas, valores, números de páginas/fls. ou teor de depoimentos.
- Toda informação inserida nos placeholders deve ser rastreável a um trecho específico do texto dos autos (`md/<base>.md`) ou da transcrição de audiência expressamente associada ao processo.
- Não atribua fala a pessoa que não esteja identificada com clareza na transcrição. Se a identidade do falante ou o teor de trecho relevante for ambíguo, use `[CONFERIR: ...]`.
- Se um dado necessário para preencher um placeholder não estiver claramente presente nos autos, NÃO o preencha: insira a marca `[CONFERIR: <descreva o que falta>]` e, ao final da resposta, liste todos os pontos que exigem confirmação do usuário.
- Não use bullet points no corpo da peça; o texto deve fluir em prosa corrida, como nos exemplos de `exemplos/`.
- Não reutilize nomes, fatos ou números dos exemplos de `exemplos/`; eles servem apenas de referência de forma.

## Processo

Primeiro, determine a lista de autos a processar:

- Se o usuário apontou arquivo(s) específico(s), use-os.
- Caso contrário, liste todos os `md/*.md` cujo **`output/<base>-alegacoes-finais.md` ainda não exista** (a menos que o usuário peça reprocessamento). A idempotência é aferida contra o sufixo **`-alegacoes-finais`** — **não** contra `output/<base>.md`, que pode ser o relatório do `esquematizar-processos` e jamais deve ser tratado como "já processado" nem sobrescrito. Se um auto de interesse ainda não tiver `md/<base>.md`, rode antes o `extrator-pdf` sobre o PDF em `input/`.

Em seguida, liste os arquivos `input/*.txt` e `input/*.md` como candidatas a transcrição e resolva
a associação processo–audiência conforme a seção **Transcrição opcional de audiência**. A
confirmação obrigatória em lote ocorre antes da leitura analítica e da redação das peças. Se não
houver transcrições candidatas, prossiga normalmente sem perguntar.

Depois, para **cada** auto selecionado, siga esta sequência antes de redigir a minuta:

1. Leia todo o `md/<base>.md` e, quando houver, toda a transcrição de audiência associada. Identifique a denúncia (e, eventualmente, seu aditamento) e a capitulação penal (artigos de lei) imputada a cada réu.
2. Resuma a imputação constante da denúncia, identificando data, hora, local e conduta atribuída a cada réu, no mesmo padrão dos exemplos de `exemplos/`.
3. Liste os documentos constantes dos autos que comprovam a materialidade (boletim de ocorrência, autos de apreensão, laudos etc.), com os respectivos números de folhas (fls.).
4. Identifique nominalmente cada vítima, testemunha, informante e réu ouvido e resuma o depoimento ou interrogatório de cada um. Havendo transcrição associada, apresente primeiro o conteúdo produzido em juízo e confronte-o, quando relevante, com as declarações da fase policial. Sem prova oral judicial, use as declarações colhidas no inquérito — isso não é pendência.
5. Verifique a folha de antecedentes criminais de cada réu para classificar como: sem antecedentes, maus antecedentes ou reincidente (e suas combinações).
6. Leia `templates/alegacoes-finais.md` e só então preencha o template, substituindo cada placeholder por texto corrido extraído dos autos.

## Estilo

Antes de redigir, leia os exemplos em `exemplos/exemplo-trafico.md` e `exemplos/exemplo-furto.md` para calibrar tom, formalidade e estrutura de parágrafos. Use-os exclusivamente como modelo de forma — os fatos, nomes e números ali contidos servem apenas de referência e nunca devem aparecer na peça final.

## Formato de saída

1. Salve cada peça final como um arquivo Markdown na pasta `output/` na raiz do diretório de trabalho atual (fora da pasta da skill), com o nome-base da origem **acrescido do sufixo `-alegacoes-finais`** (ex.: `md/1502524-61.2024.8.26.0599.md` → `output/1502524-61.2024.8.26.0599-alegacoes-finais.md`). É esse sufixo que (a) permite pular, na próxima execução, os autos já processados e (b) evita colidir com o relatório do `esquematizar-processos`, que ocupa `output/<base>.md`. Os placeholders devem estar substituídos por texto corrido, sem chaves nem marcações visíveis. Se essa pasta não existir ou não for acessível no ambiente atual, gere o arquivo `.md` para download.
2. Se o usuário tiver apontado um único auto, apresente também a peça completa na resposta. Em processamento de lote com vários autos, não despeje todas as peças na resposta — apenas salve os arquivos e resuma.
3. Ao final da resposta, informe quantos autos foram processados, quantos foram ignorados (já tinham minuta) e os nomes das minutas geradas. Indique também, por processo, qual transcrição foi utilizada e quais candidatas permaneceram sem associação. Se houver algum `[CONFERIR: ...]` nas peças, liste de forma curta e objetiva as pendências que o usuário precisa confirmar antes do protocolo, indicando a qual minuta cada pendência pertence.
