"""Contract tests: validam cada linha JSON dos fixtures NDJSON contra os schemas.

Os arquivos em data/exemplos-mqtt/ contem defeitos intencionais (duplicata,
fora de ordem, rpm=0). Nenhum deles e invalido no nivel de schema — o
tratamento de duplicatas e ordenacao pertence ao consumidor (Fase 5).
"""

import json
from pathlib import Path
from typing import Any

from oee_textil.schemas.mensagens import (
    MensagemMQTT,
    ProducaoV1,
    TelemetriaV1,
)

DATA_DIR = Path("data/exemplos-mqtt")


def load_ndjson(path: Path) -> list[dict[str, Any]]:
    """Le um arquivo NDJSON, ignorando comentarios (//) e linhas vazias.

    Retorna uma lista de dicionarios JSON.
    """
    mensagens: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("//"):
            continue
        mensagens.append(json.loads(stripped))
    return mensagens


# ---------------------------------------------------------------------------
# telemetria.ndjson
# ---------------------------------------------------------------------------


def test_telemetria_ndjson_todas_linhas_validas() -> None:
    """Cada linha JSON de telemetria.ndjson deve validar como TelemetriaV1."""
    mensagens = load_ndjson(DATA_DIR / "telemetria.ndjson")
    assert len(mensagens) >= 4, (
        f"Esperado >= 4 linhas JSON, encontrado {len(mensagens)}"
    )
    for i, msg in enumerate(mensagens):
        validated = TelemetriaV1(**msg)
        assert validated.schema == "telemetria.v1", f"Linha {i}: schema inesperado"


def test_telemetria_rpm_zero_presente() -> None:
    """Deve haver pelo menos uma linha com rpm=0 (defeito intencional)."""
    mensagens = load_ndjson(DATA_DIR / "telemetria.ndjson")
    rpms = [m["rpm"] for m in mensagens]
    assert 0.0 in rpms, "Fixture deve conter rpm=0 (maquina parada)"


# ---------------------------------------------------------------------------
# estado-parada.ndjson (dois schemas no mesmo arquivo)
# ---------------------------------------------------------------------------


def test_estado_parada_ndjson_todas_linhas_validas() -> None:
    """Cada linha de estado-parada.ndjson deve validar via MensagemMQTT."""
    mensagens = load_ndjson(DATA_DIR / "estado-parada.ndjson")
    assert len(mensagens) >= 5, (
        f"Esperado >= 5 linhas JSON, encontrado {len(mensagens)}"
    )
    for i, msg in enumerate(mensagens):
        validated = MensagemMQTT.validate_python(msg)
        assert validated.schema in ("estado.v1", "parada.v1"), (
            f"Linha {i}: schema={validated.schema} nao esperado neste arquivo"
        )


def test_estado_parada_duplicata_presente() -> None:
    """Deve haver linhas duplicadas (defeito intencional — idempotencia)."""
    mensagens = load_ndjson(DATA_DIR / "estado-parada.ndjson")
    paradas = [m for m in mensagens if m["schema"] == "parada.v1"]
    # As linhas 6 e 7 sao identicas (mesma parada QBR_AGULHA)
    assert len(paradas) == 2, (
        f"Esperado 2 eventos de parada (um duplicado), encontrado {len(paradas)}"
    )
    assert paradas[0] == paradas[1], (
        "As duas paradas devem ser identicas (duplicata intencional)"
    )


def test_estado_parada_out_of_order_presente() -> None:
    """A ultima linha do arquivo tem ts_sensor anterior (fora de ordem)."""
    mensagens = load_ndjson(DATA_DIR / "estado-parada.ndjson")
    # Ultima linha: ts_sensor 13:44:59.500 — anterior as demais (13:45:00+)
    ultima = mensagens[-1]
    primeira = mensagens[0]
    assert ultima["ts_sensor"] < primeira["ts_sensor"], (
        f"Ultima linha ({ultima['ts_sensor']}) deve ser anterior "
        f"a primeira ({primeira['ts_sensor']}) — late event intencional"
    )


# ---------------------------------------------------------------------------
# producao.ndjson
# ---------------------------------------------------------------------------


def test_producao_ndjson_todas_linhas_validas() -> None:
    """Cada linha JSON de producao.ndjson deve validar como ProducaoV1."""
    mensagens = load_ndjson(DATA_DIR / "producao.ndjson")
    assert len(mensagens) >= 3, (
        f"Esperado >= 3 linhas JSON, encontrado {len(mensagens)}"
    )
    for i, msg in enumerate(mensagens):
        validated = ProducaoV1(**msg)
        assert validated.schema == "producao.v1", f"Linha {i}: schema inesperado"
        assert validated.unidades_produzidas >= 0
        assert validated.unidades_refugo >= 0


def test_producao_refugo_positivo() -> None:
    """Deve haver refugo > 0 na primeira linha (cenario real)."""
    mensagens = load_ndjson(DATA_DIR / "producao.ndjson")
    assert mensagens[0]["unidades_refugo"] > 0, (
        "Primeiro evento de producao deve ter refugo > 0"
    )
