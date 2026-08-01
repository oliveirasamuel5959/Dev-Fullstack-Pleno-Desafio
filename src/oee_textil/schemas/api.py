"""Schemas Pydantic de resposta da API.

Modelos de saida (response) para os endpoints REST.
Separados dos modelos ORM — serializacao explicita.
"""

import datetime

from pydantic import BaseModel, Field

# --- OEE ---


class FatoresOee(BaseModel):
    """Tres fatores do OEE."""

    disponibilidade: float = Field(examples=[0.875])
    performance: float = Field(examples=[0.95])
    qualidade: float = Field(examples=[0.95])


class OeeResponse(BaseModel):
    """Resposta do endpoint OEE atual."""

    maquina_id: str = Field(examples=["TEAR-G1-L2-07"])
    janela_inicio: datetime.datetime | None = None
    janela_fim: datetime.datetime | None = None
    fatores: FatoresOee
    oee: float = Field(examples=[0.79])
    unidades_produzidas: int | None = None
    unidades_refugo: int | None = None
    tempo_planejado_s: float | None = None
    tempo_rodando_s: float | None = None


class OeeAgregadoResponse(BaseModel):
    """OEE agregado por galpao ou linha."""

    agregacao: str = Field(examples=["G1"])
    nivel: str = Field(examples=["galpao"])
    oee_medio: float = Field(examples=[0.72])
    maquinas_count: int = Field(examples=[12])
    fatores_medios: FatoresOee


class OeeSerieItem(BaseModel):
    """Um ponto na serie temporal de OEE."""

    maquina_id: str
    janela_inicio: datetime.datetime
    janela_fim: datetime.datetime
    oee: float
    disponibilidade: float
    performance: float
    qualidade: float


# --- Perdas ---


class PerdasResponse(BaseModel):
    """Analise de perdas D/P/Q."""

    maquina_id: str
    fatores: FatoresOee
    maior_perda: str = Field(examples=["Disponibilidade"])
    perda_percentual: float = Field(examples=[12.5])


# --- Pareto ---


class ParetoItem(BaseModel):
    """Um item no Pareto de paradas."""

    motivo_codigo: str = Field(examples=["QBR_AGULHA"])
    motivo_descricao: str = Field(examples=["Quebra de agulha"])
    ocorrencias: int = Field(examples=[15])
    planejada: bool = False


class ParetoResponse(BaseModel):
    """Resposta do endpoint de Pareto."""

    items: list[ParetoItem]
    periodo_inicio: datetime.datetime
    periodo_fim: datetime.datetime


# --- Estado ao vivo ---


class EstadoItem(BaseModel):
    """Estado atual de uma maquina."""

    maquina_id: str
    galpao: str
    linha: str
    tipo: str
    estado: str = Field(examples=["rodando"])
    ts_ultimo_evento: datetime.datetime | None = None


class EstadoResponse(BaseModel):
    """Resposta do endpoint de estado ao vivo."""

    maquinas: list[EstadoItem]
    total: int
    rodando: int
    parado: int
