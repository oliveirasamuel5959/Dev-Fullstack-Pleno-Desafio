"""Testes unitarios dos modelos Pydantic de contrato MQTT."""

import pytest
from pydantic import ValidationError

from oee_textil.schemas.mensagens import (
    EstadoV1,
    MensagemMQTT,
    ParadaV1,
    ProducaoV1,
    TelemetriaV1,
)

# ---------------------------------------------------------------------------
# TelemetriaV1
# ---------------------------------------------------------------------------

TELEMETRIA_VALIDA = {
    "schema": "telemetria.v1",
    "maquina_id": "TEAR-G1-L2-07",
    "ts_sensor": "2026-03-10T13:45:02.140Z",
    "rpm": 118.4,
    "voltas_acumuladas": 90418223,
    "temperatura_c": 41.2,
    "vibracao_mm_s": 2.1,
}


def test_telemetria_valida() -> None:
    """Dados validos devem instanciar sem erro."""
    t = TelemetriaV1(**TELEMETRIA_VALIDA)
    assert t.maquina_id == "TEAR-G1-L2-07"
    assert t.rpm == 118.4


def test_telemetria_rpm_zero_valido() -> None:
    """rpm=0 e valido (maquina parada)."""
    data = {**TELEMETRIA_VALIDA, "rpm": 0.0}
    t = TelemetriaV1(**data)
    assert t.rpm == 0.0


def test_telemetria_rpm_negativo_invalido() -> None:
    """rpm negativo deve falhar validacao."""
    data = {**TELEMETRIA_VALIDA, "rpm": -1.0}
    with pytest.raises(ValidationError):
        TelemetriaV1(**data)


def test_telemetria_schema_errado_invalido() -> None:
    """schema diferente do Literal deve falhar."""
    data = {**TELEMETRIA_VALIDA, "schema": "telemetria.v2"}
    with pytest.raises(ValidationError):
        TelemetriaV1(**data)


def test_telemetria_campo_ausente_invalido() -> None:
    """Campo obrigatorio ausente deve falhar."""
    data = {k: v for k, v in TELEMETRIA_VALIDA.items() if k != "ts_sensor"}
    with pytest.raises(ValidationError):
        TelemetriaV1(**data)


def test_telemetria_tipo_errado_invalido() -> None:
    """Tipo errado (string em float) deve falhar."""
    data = {**TELEMETRIA_VALIDA, "rpm": "cento e vinte"}
    with pytest.raises(ValidationError):
        TelemetriaV1(**data)


# ---------------------------------------------------------------------------
# EstadoV1
# ---------------------------------------------------------------------------

ESTADO_VALIDO = {
    "schema": "estado.v1",
    "maquina_id": "TEAR-G1-L2-07",
    "ts_sensor": "2026-03-10T13:45:00.000Z",
    "estado": "parado",
    "estado_anterior": "rodando",
}


def test_estado_valido() -> None:
    """Estado valido deve instanciar."""
    e = EstadoV1(**ESTADO_VALIDO)
    assert e.estado == "parado"


def test_estado_invalido() -> None:
    """Estado fora do Literal deve falhar."""
    data = {**ESTADO_VALIDO, "estado": "quebrado"}
    with pytest.raises(ValidationError):
        EstadoV1(**data)


def test_estado_anterior_invalido() -> None:
    """estado_anterior fora do Literal deve falhar."""
    data = {**ESTADO_VALIDO, "estado_anterior": "inexistente"}
    with pytest.raises(ValidationError):
        EstadoV1(**data)


# ---------------------------------------------------------------------------
# ParadaV1
# ---------------------------------------------------------------------------

PARADA_VALIDA = {
    "schema": "parada.v1",
    "maquina_id": "TEAR-G1-L2-07",
    "ts_sensor": "2026-03-10T13:45:00.000Z",
    "motivo_codigo": "QBR_AGULHA",
    "motivo_descricao": "Quebra de agulha",
    "planejada": False,
}


def test_parada_valida() -> None:
    """Parada valida deve instanciar."""
    p = ParadaV1(**PARADA_VALIDA)
    assert p.planejada is False


def test_parada_planejada() -> None:
    """Parada planejada deve ter planejada=True."""
    data = {**PARADA_VALIDA, "planejada": True}
    p = ParadaV1(**data)
    assert p.planejada is True


# ---------------------------------------------------------------------------
# ProducaoV1
# ---------------------------------------------------------------------------

PRODUCAO_VALIDA = {
    "schema": "producao.v1",
    "maquina_id": "TEAR-G1-L2-07",
    "ts_sensor": "2026-03-10T14:00:00.000Z",
    "unidades_produzidas": 21500,
    "unidades_refugo": 900,
    "ordem_producao": "OP-2026-00871",
}


def test_producao_valida() -> None:
    """Producao valida deve instanciar."""
    p = ProducaoV1(**PRODUCAO_VALIDA)
    assert p.unidades_produzidas == 21500


def test_producao_refugo_negativo_invalido() -> None:
    """Refugo negativo deve falhar."""
    data = {**PRODUCAO_VALIDA, "unidades_refugo": -1}
    with pytest.raises(ValidationError):
        ProducaoV1(**data)


# ---------------------------------------------------------------------------
# MensagemMQTT — discriminated union
# ---------------------------------------------------------------------------


def test_union_despacha_telemetria() -> None:
    """Union deve despachar TelemetriaV1 pelo campo schema."""
    msg = MensagemMQTT.validate_python(TELEMETRIA_VALIDA)
    assert isinstance(msg, TelemetriaV1)


def test_union_despacha_estado() -> None:
    """Union deve despachar EstadoV1 pelo campo schema."""
    msg = MensagemMQTT.validate_python(ESTADO_VALIDO)
    assert isinstance(msg, EstadoV1)


def test_union_despacha_parada() -> None:
    """Union deve despachar ParadaV1 pelo campo schema."""
    msg = MensagemMQTT.validate_python(PARADA_VALIDA)
    assert isinstance(msg, ParadaV1)


def test_union_despacha_producao() -> None:
    """Union deve despachar ProducaoV1 pelo campo schema."""
    msg = MensagemMQTT.validate_python(PRODUCAO_VALIDA)
    assert isinstance(msg, ProducaoV1)


def test_union_schema_desconhecido_invalido() -> None:
    """Schema desconhecido deve falhar na union."""
    data = {**TELEMETRIA_VALIDA, "schema": "desconhecido.v9"}
    with pytest.raises(ValidationError):
        MensagemMQTT.validate_python(data)


def test_union_schema_ausente_invalido() -> None:
    """Sem campo schema deve falhar na union."""
    data = {k: v for k, v in TELEMETRIA_VALIDA.items() if k != "schema"}
    with pytest.raises(ValidationError):
        MensagemMQTT.validate_python(data)
