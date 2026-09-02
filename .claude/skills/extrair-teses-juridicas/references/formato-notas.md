# Contrato das notas de teses

## Critérios de seleção

Extraia somente teses que, cumulativamente:

- tenham fundamentação jurídica consistente, e não sejam meras alegações factuais;
- sejam aplicáveis a outros casos, independentemente dos fatos concretos;
- contenham raciocínio estruturado, e não citação isolada sem articulação argumentativa;
- agreguem valor argumentativo real.

Cada nota deve conter uma única tese autônoma. Duas teses só são a mesma quando compartilham o
mesmo fundamento jurídico central. Temas próximos com fundamentos distintos permanecem em notas
separadas — por exemplo, cadeia de custódia por falha de lacração e por descontinuidade da guarda.

Elimine duplicatas dentro da mesma origem. Não trate como duplicadas teses que apenas dividam o
tema, mas sustentem conclusões por fundamentos jurídicos diferentes.

Se houver mais de uma peça na origem, determine `tipo_peca_origem` individualmente para cada
tese. Se não houver tese selecionável, produza somente a frase especificada no `SKILL.md`; não
gere nota vazia.

## Sanitização

Remova ou generalize, no título, no corpo e em todos os metadados exceto `processo_origem`:

- nomes de pessoas, substituindo-os por papéis como “o acusado”, “a vítima”, “a testemunha” ou
  “o apelante”;
- datas, locais, valores e demais detalhes factuais únicos do caso;
- números de processo e referências a folhas, páginas ou documentos dos autos;
- o nome do arquivo de origem e qualquer fragmento derivado dele.

O número do processo pode aparecer uma única vez, em `processo_origem`. Nunca o utilize no campo
`arquivo` nem no corpo.

Preserve:

- o fundamento jurídico e a estrutura argumentativa;
- dispositivos legais;
- citações jurisprudenciais completas tal como constam da origem, inclusive tribunal, órgão,
  relator, número e data.

Sanitizar não significa inventar uma nova fundamentação nem introduzir fatos hipotéticos. Retire
os detalhes individualizantes e faça apenas os ajustes linguísticos necessários para que o
raciocínio se sustente como tese autônoma.

## Formato de cada nota

No staging (`output/<base>-teses.md`), cada tese aparece em seu próprio bloco cercado, aberto
por ```` ```markdown ```` e fechado por ```` ``` ````. Não escreva texto de transição entre
blocos. O conteúdo interno deve ser Markdown puro e idêntico ao que vai para a nota final.

Em `output/teses/<arquivo>.md`, grave o mesmo conteúdo sem as cercas: o arquivo começa
diretamente no `---` do frontmatter. É essa versão solta, sem cerca, que o Obsidian indexa —
dentro de um bloco de código, wikilinks e frontmatter ficam inertes e nenhuma nota entra no
grafo.

Dentro do bloco, use frontmatter YAML real, delimitado por `---` em linhas próprias. Mantenha os
campos exatamente nesta ordem:

```yaml
---
arquivo: "slug-derivado-exclusivamente-do-titulo"
titulo: "Título curto da tese"
area_direito: "Direito Processual Penal"
tema: "Categoria específica e reutilizável"
tags: ["tag-kebab-case", "ramo/subtema"]
tipo_peca_origem: "Tipo da peça"
processo_origem: ""
jurisprudencia: ["[[Nome curto - Tribunal]]"]
legislacao: ["[[Art. X, diploma legal]]"]
relacionadas: []
---
```

Regras dos campos:

- `arquivo`: derive exclusivamente de `titulo`; use minúsculas, remova acentos e caracteres
  especiais, troque espaços por hífens, compacte hífens repetidos e limite a 60 caracteres. Não
  inclua processo, data ou nome da origem. Evite cortar palavra quando puder encurtar o título.
- `titulo`: título jurídico curto e autônomo, sem referência ao caso concreto.
- `area_direito`: ramo do direito com grafia estável entre execuções; prefira denominações
  canônicas como `Direito Processual Penal`.
- `tema`: subtema específico, reutilizável por outras teses e diferente do título.
- `tags`: de duas a cinco tags em kebab-case, sem espaços; admita hierarquia com `/`.
- `tipo_peca_origem`: tipo identificável da peça que contém a tese. Não invente se o texto não
  permitir a identificação; use `Tipo não identificado`.
- `processo_origem`: número do processo se identificável; caso contrário, string vazia.
- `jurisprudencia`: wikilinks dos precedentes efetivamente usados na tese; lista vazia se não
  houver.
- `legislacao`: wikilinks dos dispositivos efetivamente usados na tese; lista vazia se não
  houver.
- `relacionadas`: sempre lista vazia.

Use aspas duplas em todo valor string, inclusive em cada item de lista. Escape no YAML aspas
duplas que façam parte do conteúdo. Listas vazias permanecem `[]`.

Após o fechamento do frontmatter, escreva a tese sanitizada em parágrafos, com linguagem jurídica
técnica e precisa, na forma argumentativa utilizável em peça. Ao mencionar jurisprudência ou
legislação no corpo, utilize exatamente o mesmo wikilink do frontmatter. Preserve a citação
integral e envolva em wikilink apenas a denominação curta do precedente ou dispositivo.

## Verificação antes de salvar

Confirme, para cada bloco:

- uma tese e um fundamento jurídico central;
- ausência de dados individualizantes fora de `processo_origem`;
- slug derivado apenas do título e com até 60 caracteres;
- YAML válido, com ordem, aspas e listas corretas;
- correspondência exata entre wikilinks do corpo e do frontmatter;
- nenhuma jurisprudência, legislação ou informação acrescentada sem suporte na origem;
- nenhuma nota duplicada na mesma saída.

