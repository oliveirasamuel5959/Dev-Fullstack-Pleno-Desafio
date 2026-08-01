"""Modelo ORM — Parada (evento de parada com motivo).

Denormalizacao deliberada: motivo_descricao e planejada sao armazenados como
estavam no momento do evento, alem da FK para motivos_parada. Se o catalogo
mudar (ex.: SETUP deixa de ser planejada), o evento historico preserva a
verdade do momento. Drift entre evento e catalogo e sinalizado, nao silencioso
(mission §4.2).

Surrogate PK (IDENTITY) — mesma justificativa de EstadoMaquina.
"""

from __future__ import annotations

import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Identity,
    Index,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from oee_textil.core.database import Base

if TYPE_CHECKING:
    from oee_textil.models.maquina import Maquina
    from oee_textil.models.motivo_parada import MotivoParada


class Parada(Base):
    """Evento de parada de maquina com motivo e classificacao."""

    __tablename__ = "parada"

    id: Mapped[int] = mapped_column(
        Integer,
        Identity(),
        primary_key=True,
    )
    maquina_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("maquinas.maquina_id"),
    )
    motivo_codigo: Mapped[str] = mapped_column(
        String(30),
        ForeignKey("motivos_parada.motivo_codigo"),
    )
    motivo_descricao: Mapped[str] = mapped_column(String(100))
    planejada: Mapped[bool] = mapped_column(Boolean)
    ts_sensor: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
    )
    ts_ingestao: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    __table_args__ = (
        Index("ix_parada_maquina_ts", "maquina_id", "ts_sensor"),
        Index("ix_parada_motivo", "motivo_codigo"),
    )

    # Relationships
    maquina: Mapped[Maquina] = relationship(
        back_populates="paradas",
    )
    motivo: Mapped[MotivoParada] = relationship(
        back_populates="paradas",
    )

    def __repr__(self) -> str:
        return (
            f"Parada(maquina_id={self.maquina_id!r}, "
            f"motivo_codigo={self.motivo_codigo!r}, "
            f"planejada={self.planejada})"
        )
