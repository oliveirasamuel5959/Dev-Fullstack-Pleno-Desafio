"""Testes de verificacao dos JSON Schema exportados em docs/contracts/."""

import json
from pathlib import Path

CONTRACTS_DIR = Path("docs/contracts")
EXPECTED_SCHEMAS = [
    "telemetria.v1.schema.json",
    "estado.v1.schema.json",
    "parada.v1.schema.json",
    "producao.v1.schema.json",
]


def test_todos_arquivos_existem() -> None:
    """Os 4 arquivos JSON Schema devem existir em docs/contracts/."""
    for nome in EXPECTED_SCHEMAS:
        path = CONTRACTS_DIR / nome
        assert path.exists(), f"Arquivo ausente: {path}"


def test_todos_sao_json_valido() -> None:
    """Cada arquivo deve ser JSON valido."""
    for nome in EXPECTED_SCHEMAS:
        path = CONTRACTS_DIR / nome
        data = json.loads(path.read_text(encoding="utf-8"))
        assert isinstance(data, dict), f"{nome} nao e um objeto JSON"


def test_cada_schema_contem_campos_esperados() -> None:
    """Cada JSON Schema deve conter title, type, properties."""
    for nome in EXPECTED_SCHEMAS:
        path = CONTRACTS_DIR / nome
        data = json.loads(path.read_text(encoding="utf-8"))
        assert "title" in data, f"{nome}: falta title"
        assert data.get("type") == "object", f"{nome}: type != object"
        assert "properties" in data, f"{nome}: falta properties"


def test_schema_field_em_properties() -> None:
    """O campo 'schema' deve estar em properties de cada JSON Schema."""
    for nome in EXPECTED_SCHEMAS:
        path = CONTRACTS_DIR / nome
        data = json.loads(path.read_text(encoding="utf-8"))
        assert "schema" in data["properties"], (
            f"{nome}: campo 'schema' ausente em properties"
        )


def test_telemetria_tem_rpm_ge_zero() -> None:
    """Telemetria deve ter restricao rpm >= 0 no JSON Schema."""
    data = json.loads(
        (CONTRACTS_DIR / "telemetria.v1.schema.json").read_text(encoding="utf-8")
    )
    rpm = data["properties"]["rpm"]
    assert rpm.get("minimum") == 0, "rpm deve ter minimum=0"
