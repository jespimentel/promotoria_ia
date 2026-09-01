from __future__ import annotations

import importlib.util
from pathlib import Path
import shutil
import sys
from types import SimpleNamespace
import unittest
from uuid import uuid4


SCRIPT = (
    Path(__file__).parents[1]
    / ".claude/skills/transcrever-midia/scripts/transcrever_midia.py"
)
SPEC = importlib.util.spec_from_file_location("transcrever_midia", SCRIPT)
assert SPEC and SPEC.loader
MODULO = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULO
SPEC.loader.exec_module(MODULO)


class ModeloFalso:
    def transcribe(self, caminho, **opcoes):
        assert Path(caminho).is_file()
        assert opcoes["language"] == "pt"
        segmentos = [SimpleNamespace(start=0.1, end=0.9, text=" teste local ")]
        info = SimpleNamespace(language="pt", language_probability=0.99)
        return segmentos, info


class TranscreverMidiaTests(unittest.TestCase):
    def test_timestamp_arredonda_e_formata(self):
        self.assertEqual(MODULO.timestamp(3661.2345), "01:01:01.234")
        self.assertEqual(MODULO.timestamp(-1), "00:00:00.000")

    def test_markdown_preserva_texto_e_timestamps(self):
        info = SimpleNamespace(language="pt", language_probability=0.98765)
        segmentos = [SimpleNamespace(start=0.0, end=1.25, text="  Olá, mundo.  ")]

        texto, quantidade = MODULO.montar_markdown(Path("audiência.mp4"), info, segmentos)

        self.assertEqual(quantidade, 1)
        self.assertIn('arquivo_origem: "audiência.mp4"', texto)
        self.assertIn("tipo_documento: transcricao_midia", texto)
        self.assertIn("processo_cnj: null", texto)
        self.assertIn("probabilidade_idioma: 0.9877", texto)
        self.assertIn("[00:00:00.000 → 00:00:01.250] Olá, mundo.", texto)

    def test_markdown_registra_ausencia_de_fala(self):
        info = SimpleNamespace(language="pt", language_probability=0.0)
        texto, quantidade = MODULO.montar_markdown(Path("silencio.wav"), info, [])
        self.assertEqual(quantidade, 0)
        self.assertIn("[Nenhuma fala reconhecida]", texto)

    def test_destino_nao_colide_com_md_do_pdf(self):
        origem = Path("input/1502524-61.2024.8.26.0599.mp4")
        destino = MODULO.destino_transcricao(origem, Path("md"))
        self.assertEqual(
            destino,
            Path("md/1502524-61.2024.8.26.0599-transcricao.md"),
        )
        self.assertNotEqual(destino, Path("md/1502524-61.2024.8.26.0599.md"))

    def test_cnj_e_registrado_no_frontmatter(self):
        origem = Path("1502524-61.2024.8.26.0599-audiencia.asf")
        info = SimpleNamespace(language="pt", language_probability=1.0)
        texto, _ = MODULO.montar_markdown(origem, info, [])
        self.assertIn('processo_cnj: "1502524-61.2024.8.26.0599"', texto)

    @unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"), "FFmpeg ausente")
    def test_pipeline_ffmpeg_com_modelo_simulado(self):
        ffmpeg, ffprobe = MODULO.executaveis_ffmpeg()
        args = SimpleNamespace(language="pt", beam_size=5, vad_filter=False)
        pasta = Path.cwd() / f".teste-transcrever-midia-{uuid4().hex}"
        pasta.mkdir()
        try:
            origem = pasta / "entrada.mp3"
            destino = pasta / "saida.md"
            processo = __import__("subprocess").run(
                [
                    ffmpeg, "-hide_banner", "-loglevel", "error", "-f", "lavfi",
                    "-i", "sine=frequency=440:duration=1", "-y", str(origem),
                ],
                check=False,
            )
            self.assertEqual(processo.returncode, 0)

            resultado = MODULO.transcrever(
                origem, destino, ModeloFalso(), ffmpeg, ffprobe, args
            )

            self.assertEqual(resultado.segmentos, 1)
            self.assertGreater(resultado.duracao, 0.9)
            self.assertIn("teste local", destino.read_text(encoding="utf-8"))
        finally:
            shutil.rmtree(pasta, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
