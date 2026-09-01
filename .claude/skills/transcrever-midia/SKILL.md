---
name: transcrever-midia
description: Transcreve localmente arquivos de áudio e vídeo de input/ (como MP3, MP4, ASF, WAV, M4A, WMA, MOV e MKV) para Markdown com sufixo -transcricao em md/, extraindo o áudio com FFmpeg e reconhecendo a fala com faster-whisper. Use ao transcrever gravações ou preparar a prova oral para análise conjunta com os autos, sem enviar o conteúdo a serviços externos.
---

# Transcrição local de mídia

Converta cada mídia em uma transcrição Markdown com timestamps. O fluxo normal é
`input/<base>.<extensão>` → `md/<base>-transcricao.md`. O sufixo é obrigatório para que uma mídia
e um PDF com o mesmo nome-base coexistam (`input/123.pdf` → `md/123.md`; `input/123.mp4` →
`md/123-transcricao.md`).

## Execução

Na raiz do projeto, execute:

```powershell
uv run python .claude/skills/transcrever-midia/scripts/transcrever_midia.py
```

Sem argumentos, o script processa todas as mídias reconhecidas em `input/` que ainda não tenham
`md/<base>-transcricao.md`. Para arquivos apontados explicitamente, passe seus caminhos; nesse
caso, a transcrição correspondente pode ser refeita. Use `--force` somente quando o usuário pedir
o reprocessamento de todo o lote.

O padrão usa o modelo `small`, idioma português, CPU e quantização `int8`, uma combinação adequada
para execução local sem GPU. Ajustes comuns:

```powershell
# Mais rápido, com menor precisão
uv run python .claude/skills/transcrever-midia/scripts/transcrever_midia.py --model base

# Mais preciso, porém mais lento e pesado
uv run python .claude/skills/transcrever-midia/scripts/transcrever_midia.py --model medium

# NVIDIA CUDA
uv run python .claude/skills/transcrever-midia/scripts/transcrever_midia.py --device cuda --compute-type float16

# Detectar o idioma automaticamente
uv run python .claude/skills/transcrever-midia/scripts/transcrever_midia.py --language auto
```

Antes da primeira execução, verifique o ambiente:

```powershell
uv run python .claude/skills/transcrever-midia/scripts/transcrever_midia.py --check-deps
```

## Privacidade e dependências

- O FFmpeg extrai uma faixa PCM mono de 16 kHz em uma pasta temporária local.
- O `faster-whisper` faz a inferência local. O áudio e a transcrição não são enviados a uma API.
- Na primeira utilização de um modelo, seus pesos são baixados da Hugging Face. Depois disso,
  `--local-files-only` impede qualquer tentativa de download e exige que o modelo já esteja em cache.
- O script requer os executáveis `ffmpeg` e `ffprobe` no `PATH` e a dependência Python
  `faster-whisper`, declarada no `pyproject.toml`.

Não envie a mídia, trechos de áudio, transcrições ou metadados a serviços externos. Se a
transcrição local falhar, relate a falha e preserve o arquivo original.

## Saída e rastreabilidade

Cada saída contém `tipo_documento: transcricao_midia`, o `processo_cnj` extraído do nome da mídia
quando disponível, metadados da origem e blocos com timestamps no formato
`[HH:MM:SS.mmm → HH:MM:SS.mmm]`. O texto é a saída literal do reconhecedor: não resuma, corrija,
complete ou interprete o conteúdo durante a extração.

Como `input/` e `md/` são planos, duas mídias com o mesmo nome-base (por exemplo, `reuniao.mp3` e
`reuniao.mp4`) colidem em `md/reuniao-transcricao.md`. O script detecta a colisão e não escolhe
uma origem silenciosamente. O MD de um PDF nunca é destino desta skill.

## Integração com alegações finais

Quando a mídia for de uma audiência vinculada a um processo, prefira incluir o número CNJ no nome,
por exemplo `1502524-61.2024.8.26.0599-audiencia.mp4`. A skill `alegacoes-finais` usa o CNJ do
frontmatter/nome para associar a transcrição ao `md/<cnj>.md`, lê ambos integralmente e gera uma
única minuta para o processo. A transcrição é fonte complementar e nunca deve ser tratada como auto
independente.

Ao final, informe quantas mídias foram processadas, ignoradas e falharam, além dos Markdown
gerados. Uma falha em um arquivo não deve impedir o restante do lote.
