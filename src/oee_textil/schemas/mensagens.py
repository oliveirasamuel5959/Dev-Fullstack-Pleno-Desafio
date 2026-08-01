"""Modelos Pydantic v2 dos 4 contratos de mensagem MQTT versionados.

Cada modelo representa um schema versionado (v1). O campo `schema` e um
Literal que discrimina o tipo de mensagem na borda do sistema.

Fonte da verdade: docs/ESPECIFICACAO_TECNICA.md secao 2.
Dados de exemplo: data/exemplos-mqtt/*.ndjson.
"""

from datetime import datetime
from typing import Annotated, Any, Literal

from pydantic import BaseModel, Field, TypeAdapter


class TelemetriaV1(BaseModel):
    """Metricas continuas de maquina (topico: .../telemetria)."""

    model_config = {"protected_namespaces": ()}

    schema: Literal["telemetria.v1"]  # type: ignore[assignment]
    maquina_id: str
    ts_sensor: datetime
    rpm: float = Field(ge=0, description="Rotacoes por minuto; 0 = maquina parada")
    voltas_acumuladas: int = Field(ge=0, description="Contador absoluto de voltas")
    temperatura_c: float = Field(description="Temperatura em graus Celsius")
    vibracao_mm_s: float = Field(ge=0, description="Vibracao em mm/s")


class EstadoV1(BaseModel):
    """Evento de mudanca de estado da maquina (topico: .../estado)."""

    model_config = {"protected_namespaces": ()}

    schema: Literal["estado.v1"]  # type: ignore[assignment]
    maquina_id: str
    ts_sensor: datetime
    estado: Literal["rodando", "parado", "setup", "manutencao"]
    estado_anterior: Literal["rodando", "parado", "setup", "manutencao"]


class ParadaV1(BaseModel):
    """Evento de parada com motivo (topico: .../parada)."""

    model_config = {"protected_namespaces": ()}

    schema: Literal["parada.v1"]  # type: ignore[assignment]
    maquina_id: str
    ts_sensor: datetime
    motivo_codigo: str = Field(description="Codigo do motivo, ex: QBR_AGULHA")
    motivo_descricao: str = Field(description="Descricao legivel do motivo")
    planejada: bool = Field(
        description="True = parada planejada (desconta do tempo planejado)"
    )


class ProducaoV1(BaseModel):
    """Contagem de producao e refugo (topico: .../producao)."""

    model_config = {"protected_namespaces": ()}

    schema: Literal["producao.v1"]  # type: ignore[assignment]
    maquina_id: str
    ts_sensor: datetime
    unidades_produzidas: int = Field(ge=0)
    unidades_refugo: int = Field(ge=0)
    ordem_producao: str = Field(description="Identificador da ordem de producao")


# TypeAdapter com union discriminada: despacha pelo campo `schema`.
# Uso: msg = MensagemMQTT.validate_python(data)  # retorna o modelo correto
MensagemMQTT: TypeAdapter[Any] = TypeAdapter(
    Annotated[
        TelemetriaV1 | EstadoV1 | ParadaV1 | ProducaoV1,
        Field(discriminator="schema"),
    ]
)
