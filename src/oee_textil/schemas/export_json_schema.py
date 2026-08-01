"""Exporta JSON Schema de cada modelo Pydantic para docs/contracts/.

Uso:
    uv run python -m oee_textil.schemas.export_json_schema
"""

import json
from pathlib import Path

from oee_textil.schemas.mensagens import (
    EstadoV1,
    ParadaV1,
    ProducaoV1,
    TelemetriaV1,
)

OUTPUT_DIR = Path("docs/contracts")

SCHEMAS = {
    "telemetria.v1": TelemetriaV1,
    "estado.v1": EstadoV1,
    "parada.v1": ParadaV1,
    "producao.v1": ProducaoV1,
}


def export_schemas() -> None:
    """Gera e escreve os 4 arquivos JSON Schema."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for nome, model in SCHEMAS.items():
        json_schema = model.model_json_schema()  # type: ignore[attr-defined]
        path = OUTPUT_DIR / f"{nome}.schema.json"
        path.write_text(
            json.dumps(json_schema, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print(f"  {path} — {len(path.read_bytes())} bytes")


if __name__ == "__main__":
    print("Exportando JSON Schema para docs/contracts/...")
    export_schemas()
    print("Concluido.")
