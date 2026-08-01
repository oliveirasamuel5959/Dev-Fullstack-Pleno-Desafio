"""Modelo ORM — Producao (evento de contagem de producao e refugo).

Surrogate PK (IDENTITY) — mesma justificativa de EstadoMaquina.
"""

from __future__ import annotations

import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
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


class Producao(Base):
    """Evento de contagem de producao e refugo por janela."""

    __tablename__ = "producao"

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
    unidades_produzidas: Mapped[int] = mapped_column(BigInteger)
    unidades_refugo: Mapped[int] = mapped_column(BigInteger)
    ordem_producao: Mapped[str] = mapped_column(String(30))
    ts_ingestao: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    content_hash: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
        unique=True,
    )

    __table_args__ = (Index("ix_producao_maquina_ts", "maquina_id", "ts_sensor"),)

    # Relationships
    maquina: Mapped[Maquina] = relationship(
        back_populates="producoes",
    )

    def __repr__(self) -> str:
        return (
            f"Producao(maquina_id={self.maquina_id!r}, "
            f"ts_sensor={self.ts_sensor}, "
            f"ordem_producao={self.ordem_producao!r})"
        )
