"""Modelo ORM — EstadoMaquina (evento de mudanca de estado).

Surrogate PK (IDENTITY) — multiplos tipos de evento por maquina x timestamp
tornam PK natural inviavel. Estrategia de dedup (hash de conteudo) chega na
Fase 5 com migracao propria.

Sem CHECK constraint em estado — a validacao dos 4 literais e na borda
(Pydantic, Fase 1). Evolucao aditiva de schema (ADR-002) nao pode exigir
migracao de constraint.
"""

from __future__ import annotations

import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Identity, Index, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from oee_textil.core.database import Base

if TYPE_CHECKING:
    from oee_textil.models.maquina import Maquina


class EstadoMaquina(Base):
    """Evento de mudanca de estado da maquina."""

    __tablename__ = "estado_maquina"

    id: Mapped[int] = mapped_column(
        Integer,
        Identity(),
        primary_key=True,
    )
    maquina_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("maquinas.maquina_id"),
    )
    ts_sensor: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
    )
    estado: Mapped[str] = mapped_column(String(20))
    estado_anterior: Mapped[str] = mapped_column(String(20))
    ts_ingestao: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    __table_args__ = (Index("ix_estado_maquina_maquina_ts", "maquina_id", "ts_sensor"),)

    # Relationships
    maquina: Mapped[Maquina] = relationship(
        back_populates="estados",
    )

    def __repr__(self) -> str:
        return (
            f"EstadoMaquina(maquina_id={self.maquina_id!r}, "
            f"ts_sensor={self.ts_sensor}, estado={self.estado!r})"
        )
