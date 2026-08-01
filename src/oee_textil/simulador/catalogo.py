"""Carregamento do catalogo de maquinas a partir de CSV.

Fonte: data/exemplos-mqtt/maquinas.csv
Uso: tabela de roteamento interno maquina_id -> (galpao, linha) para
construcao dos topicos MQTT na topologia fabrica/{galpao}/{linha}/{maquina}/...
"""

import csv
from pathlib import Path


def carregar_catalogo(data_dir: str | Path) -> dict[str, tuple[str, str]]:
    """Le maquinas.csv e retorna {maquina_id: (galpao, linha)}.

    Args:
        data_dir: Diretorio que contem maquinas.csv.

    Returns:
        Dicionario mapeando maquina_id para (galpao, linha).

    Raises:
        FileNotFoundError: Se maquinas.csv nao existir no data_dir.
    """
    csv_path = Path(data_dir) / "maquinas.csv"

    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(
            (linha for linha in f if not linha.startswith("#")),
        )

        return {row["maquina_id"]: (row["galpao"], row["linha"]) for row in reader}
