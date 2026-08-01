"""Leitor de arquivos NDJSON de exemplo.

Le os 3 arquivos NDJSON (telemetria, estado-parada, producao) do diretorio
de dados, filtra comentarios e linhas vazias, e retorna uma lista plana de
mensagens como dicts.
"""

import json
import sys
from pathlib import Path
from typing import Any


def _parse_ndjson(caminho: Path) -> list[dict[str, Any]]:
    """Le um arquivo NDJSON e retorna lista de dicts."""
    mensagens: list[dict[str, Any]] = []

    if not caminho.exists():
        print(f"[AVISO] Arquivo nao encontrado: {caminho}", file=sys.stderr)
        return mensagens

    with open(caminho, encoding="utf-8") as f:
        for num_linha, linha in enumerate(f, start=1):
            stripped = linha.strip()

            # Ignorar comentarios e linhas vazias
            if not stripped or stripped.startswith("//"):
                continue

            try:
                msg = json.loads(stripped)
                mensagens.append(msg)
            except json.JSONDecodeError as e:
                print(
                    f"[AVISO] Linha {num_linha} JSON invalido em {caminho.name}: {e}",
                    file=sys.stderr,
                )
                continue

    return mensagens


def carregar_mensagens(data_dir: str | Path) -> list[dict[str, Any]]:
    """Le os 3 arquivos NDJSON e retorna lista plana de mensagens.

    Ordem de leitura: telemetria.ndjson, estado-parada.ndjson, producao.ndjson.

    Args:
        data_dir: Diretorio que contem os arquivos .ndjson.

    Returns:
        Lista de dicts, cada um representando uma mensagem JSON valida.
    """
    data_path = Path(data_dir)
    arquivos = [
        "telemetria.ndjson",
        "estado-parada.ndjson",
        "producao.ndjson",
    ]

    todas: list[dict[str, Any]] = []

    for nome in arquivos:
        caminho = data_path / nome
        mensagens = _parse_ndjson(caminho)
        todas.extend(mensagens)

    return todas
