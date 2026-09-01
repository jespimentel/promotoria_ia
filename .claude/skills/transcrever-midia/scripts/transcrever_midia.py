"""Transcreve áudio/vídeo localmente com FFmpeg e faster-whisper."""

from __future__ import annotations

import argparse
from contextlib import contextmanager
from dataclasses import dataclass
from importlib.metadata import PackageNotFoundError, version
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
from typing import Any, Iterable
from uuid import uuid4


EXTENSOES_SUPORTADAS = {
    ".3gp", ".aac", ".aif", ".aiff", ".amr", ".asf", ".avi", ".caf",
    ".flac", ".m2ts", ".m4a", ".m4v", ".mka", ".mkv", ".mov", ".mp3",
    ".mp4", ".mpeg", ".mpg", ".mts", ".oga", ".ogg", ".opus", ".ts",
    ".wav", ".webm", ".wma", ".wmv",
}
PADRAO_CNJ = re.compile(r"(?<!\d)(\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4})(?!\d)")


@dataclass
class Resultado:
    origem: Path
    destino: Path
    segmentos: int
    duracao: float
    idioma: str
    probabilidade_idioma: float


def argumentos() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Transcreve localmente mídias de input/ para Markdown em md/."
    )
    parser.add_argument(
        "midias",
        nargs="*",
        type=Path,
        help="Mídias específicas. Sem argumentos, processa input/ de forma idempotente.",
    )
    parser.add_argument("--input-dir", type=Path, default=Path("input"))
    parser.add_argument("--output-dir", type=Path, default=Path("md"))
    parser.add_argument("--model", default="small", help="Modelo Whisper (padrão: small).")
    parser.add_argument("--language", default="pt", help="Idioma ISO 639-1 ou 'auto' (padrão: pt).")
    parser.add_argument("--device", choices=("cpu", "cuda", "auto"), default="cpu")
    parser.add_argument("--compute-type", default="int8", help="Tipo do CTranslate2 (padrão: int8).")
    parser.add_argument("--beam-size", type=int, default=5)
    parser.add_argument("--vad-filter", action="store_true", help="Ativa filtro de silêncio do Whisper.")
    parser.add_argument("--model-dir", type=Path, help="Cache local dos modelos Whisper.")
    parser.add_argument(
        "--local-files-only",
        action="store_true",
        help="Não baixa pesos; exige que o modelo já esteja no cache.",
    )
    parser.add_argument("--force", action="store_true", help="Reprocessa saídas existentes no lote.")
    parser.add_argument("--check-deps", action="store_true", help="Verifica dependências e encerra.")
    return parser.parse_args()


def executaveis_ffmpeg() -> tuple[str, str]:
    ffmpeg = shutil.which("ffmpeg")
    ffprobe = shutil.which("ffprobe")
    ausentes = [nome for nome, caminho in (("ffmpeg", ffmpeg), ("ffprobe", ffprobe)) if not caminho]
    if ausentes:
        raise RuntimeError("executável(is) ausente(s) no PATH: " + ", ".join(ausentes))
    return ffmpeg, ffprobe


def versao_whisper() -> str:
    try:
        return version("faster-whisper")
    except PackageNotFoundError as exc:
        raise RuntimeError(
            "faster-whisper não está instalado; sincronize o ambiente com 'uv sync'"
        ) from exc


def carregar_classe_whisper():
    try:
        from faster_whisper import WhisperModel
    except (ImportError, OSError) as exc:
        raise RuntimeError(f"não foi possível carregar faster-whisper: {exc}") from exc
    return WhisperModel


def validar_argumentos(args: argparse.Namespace) -> None:
    if args.beam_size < 1:
        raise RuntimeError("--beam-size deve ser maior que zero")
    if not args.language.strip():
        raise RuntimeError("--language não pode ser vazio")


def selecionar_midias(args: argparse.Namespace) -> tuple[list[Path], bool]:
    explicitas = bool(args.midias)
    if explicitas:
        selecionadas = args.midias
    else:
        selecionadas = sorted(
            (p for p in args.input_dir.iterdir() if p.is_file() and p.suffix.lower() in EXTENSOES_SUPORTADAS),
            key=lambda p: p.name.casefold(),
        ) if args.input_dir.is_dir() else []

    invalidas = [
        str(p) for p in selecionadas
        if not p.is_file() or p.suffix.lower() not in EXTENSOES_SUPORTADAS
    ]
    if invalidas:
        raise RuntimeError("mídia(s) inexistente(s) ou não suportada(s): " + ", ".join(invalidas))

    bases: dict[str, list[Path]] = {}
    for caminho in selecionadas:
        bases.setdefault(caminho.stem.casefold(), []).append(caminho)
    colisoes = [grupo for grupo in bases.values() if len(grupo) > 1]
    if colisoes:
        detalhes = "; ".join(", ".join(str(p) for p in grupo) for grupo in colisoes)
        raise RuntimeError("mídias com o mesmo nome-base gerariam a mesma saída: " + detalhes)
    return selecionadas, explicitas


def numero_cnj(caminho: Path) -> str | None:
    correspondencia = PADRAO_CNJ.search(caminho.stem)
    return correspondencia.group(1) if correspondencia else None


def destino_transcricao(origem: Path, pasta_saida: Path) -> Path:
    """Mantém transcrições distintas do MD dos autos, mesmo com o mesmo nome-base."""
    return pasta_saida / f"{origem.stem}-transcricao.md"


def duracao_midia(ffprobe: str, origem: Path) -> float:
    processo = subprocess.run(
        [
            ffprobe, "-v", "error", "-select_streams", "a:0",
            "-show_entries", "stream=duration:format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", str(origem),
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if processo.returncode != 0:
        detalhe = " ".join((processo.stderr or processo.stdout).split())
        raise RuntimeError("ffprobe não conseguiu ler a mídia: " + (detalhe or "erro desconhecido"))
    valores = []
    for linha in processo.stdout.splitlines():
        try:
            valores.append(float(linha.strip()))
        except ValueError:
            continue
    if not valores:
        raise RuntimeError("a mídia não contém uma faixa de áudio com duração identificável")
    return max(valores)


def extrair_audio(ffmpeg: str, origem: Path, destino_wav: Path) -> None:
    processo = subprocess.run(
        [
            ffmpeg, "-hide_banner", "-loglevel", "error", "-nostdin", "-y",
            "-i", str(origem), "-map", "0:a:0", "-vn", "-ac", "1", "-ar", "16000",
            "-c:a", "pcm_s16le", str(destino_wav),
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if processo.returncode != 0 or not destino_wav.is_file():
        detalhe = " ".join((processo.stderr or processo.stdout).split())
        raise RuntimeError("FFmpeg não conseguiu extrair o áudio: " + (detalhe or "erro desconhecido"))


def timestamp(segundos: float) -> str:
    milissegundos = max(0, round(segundos * 1000))
    horas, resto = divmod(milissegundos, 3_600_000)
    minutos, resto = divmod(resto, 60_000)
    segundos_inteiros, millis = divmod(resto, 1000)
    return f"{horas:02d}:{minutos:02d}:{segundos_inteiros:02d}.{millis:03d}"


def montar_markdown(origem: Path, info: Any, segmentos: Iterable[Any]) -> tuple[str, int]:
    idioma = str(getattr(info, "language", "desconhecido"))
    probabilidade = float(getattr(info, "language_probability", 0.0))
    linhas = [
        "---",
        f"arquivo_origem: {json.dumps(origem.name, ensure_ascii=False)}",
        "tipo_documento: transcricao_midia",
        f"processo_cnj: {json.dumps(numero_cnj(origem), ensure_ascii=False)}",
        "motor: faster-whisper",
        f"idioma_detectado: {idioma}",
        f"probabilidade_idioma: {probabilidade:.4f}",
        "---",
        "",
        "# Transcrição",
        "",
    ]
    quantidade = 0
    for segmento in segmentos:
        texto = str(segmento.text).strip()
        if not texto:
            continue
        linhas.append(f"[{timestamp(float(segmento.start))} → {timestamp(float(segmento.end))}] {texto}")
        linhas.append("")
        quantidade += 1
    if quantidade == 0:
        linhas.extend(["[Nenhuma fala reconhecida]", ""])
    return "\n".join(linhas), quantidade


@contextmanager
def pasta_temporaria(pasta_pai: Path):
    caminho = pasta_pai / f".transcrever-midia-{uuid4().hex}"
    caminho.mkdir(parents=True)
    try:
        yield caminho
    finally:
        shutil.rmtree(caminho, ignore_errors=True)


def transcrever(
    origem: Path,
    destino: Path,
    modelo: Any,
    ffmpeg: str,
    ffprobe: str,
    args: argparse.Namespace,
) -> Resultado:
    destino.parent.mkdir(parents=True, exist_ok=True)
    duracao = duracao_midia(ffprobe, origem)
    with pasta_temporaria(destino.parent) as temporario:
        wav = temporario / "audio.wav"
        extrair_audio(ffmpeg, origem, wav)
        segmentos, info = modelo.transcribe(
            str(wav),
            language=None if args.language.casefold() == "auto" else args.language,
            beam_size=args.beam_size,
            vad_filter=args.vad_filter,
        )
        conteudo, quantidade = montar_markdown(origem, info, segmentos)

    temporario_saida = destino.with_suffix(destino.suffix + ".tmp")
    temporario_saida.write_text(conteudo, encoding="utf-8")
    temporario_saida.replace(destino)
    return Resultado(
        origem=origem,
        destino=destino,
        segmentos=quantidade,
        duracao=duracao,
        idioma=str(getattr(info, "language", "desconhecido")),
        probabilidade_idioma=float(getattr(info, "language_probability", 0.0)),
    )


def main() -> int:
    args = argumentos()
    try:
        validar_argumentos(args)
        ffmpeg, ffprobe = executaveis_ffmpeg()
        versao = versao_whisper()
    except RuntimeError as exc:
        print(f"ERRO DE DEPENDÊNCIA: {exc}", file=sys.stderr)
        return 2

    if args.check_deps:
        try:
            carregar_classe_whisper()
        except RuntimeError as exc:
            print(f"ERRO DE DEPENDÊNCIA: {exc}", file=sys.stderr)
            return 2
        print(f"Dependências disponíveis: faster-whisper {versao}; FFmpeg {ffmpeg}; ffprobe {ffprobe}.")
        return 0

    try:
        midias, explicitas = selecionar_midias(args)
    except RuntimeError as exc:
        print(f"ERRO: {exc}", file=sys.stderr)
        return 2

    pendentes: list[tuple[Path, Path]] = []
    ignoradas: list[Path] = []
    for origem in midias:
        destino = destino_transcricao(origem, args.output_dir)
        if destino.exists() and not (args.force or explicitas):
            ignoradas.append(origem)
        else:
            pendentes.append((origem, destino))

    if not pendentes:
        print(f"RESUMO processados=0 ignorados={len(ignoradas)} falhas=0")
        return 0

    try:
        WhisperModel = carregar_classe_whisper()
        opcoes_modelo: dict[str, Any] = {
            "device": args.device,
            "compute_type": args.compute_type,
            "local_files_only": args.local_files_only,
        }
        if args.model_dir:
            opcoes_modelo["download_root"] = str(args.model_dir)
        modelo = WhisperModel(args.model, **opcoes_modelo)
    except Exception as exc:
        print(f"ERRO AO CARREGAR MODELO '{args.model}': {exc}", file=sys.stderr)
        return 2

    processados: list[Resultado] = []
    falhas = 0
    for origem, destino in pendentes:
        try:
            processados.append(transcrever(origem, destino, modelo, ffmpeg, ffprobe, args))
        except Exception as exc:
            falhas += 1
            print(f"FALHA {origem}: {exc}", file=sys.stderr)

    for item in processados:
        print(
            f"GERADO {item.destino} | segmentos={item.segmentos} duração={item.duracao:.1f}s "
            f"idioma={item.idioma} probabilidade={item.probabilidade_idioma:.4f}"
        )
    print(
        f"RESUMO processados={len(processados)} ignorados={len(ignoradas)} falhas={falhas}"
    )
    return 1 if falhas else 0


if __name__ == "__main__":
    raise SystemExit(main())
