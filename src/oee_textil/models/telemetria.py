"""Modelo ORM — Telemetria (hypertable TimescaleDB).

Metricas continuas de maquina. Particionada por ts_sensor (by_range).
PK natural (maquina_id, ts_sensor) — um sensor publica no maximo 1 leitura
por tick. O consumidor (Fase 5) usa ON CONFLICT DO NOTHING para idempotencia.

Coluna de particionamento: ts_sensor (TIMESTAMPTZ).
Chunk default de 7 dias (padrao TimescaleDB) — suficiente para o skeleton.
"""

from __future__ import annotations

import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, DateTime, Float, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from oee_textil.core.database import Base

if TYPE_CHECKING:
    from oee_textil.models.maquina import Maquina


class Telemetria(Base):
    """Metricas continuas de maquina — hypertable TimescaleDB."""

    __tablename__ = "telemetria"

    maquina_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("maquinas.maquina_id"),
        primary_key=True,
    )
    ts_sensor: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        primary_key=True,
    )
    rpm: Mapped[float] = mapped_column(Float)
    voltas_acumuladas: Mapped[int] = mapped_column(BigInteger)
    temperatura_c: Mapped[float] = mapped_column(Float)
    vibracao_mm_s: Mapped[float] = mapped_column(Float)
    ts_ingestao: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    # Relationships
    maquina: Mapped[Maquina] = relationship(
        back_populates="telemetrias",
    )

    def __repr__(self) -> str:
        return (
            f"Telemetria(maquina_id={self.maquina_id!r}, "
            f"ts_sensor={self.ts_sensor}, rpm={self.rpm})"
        )
