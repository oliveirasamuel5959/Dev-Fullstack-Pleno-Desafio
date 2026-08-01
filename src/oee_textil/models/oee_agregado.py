"""Modelo ORM — OeeAgregado (agregacao materializada de OEE).

Armazena o resultado do calculo de OEE por maquina x janela de tempo.
UNIQUE (maquina_id, janela_inicio, janela_fim) permite upsert idempotente
via ON CONFLICT DO NOTHING ou ON CONFLICT UPDATE.

Populado pelo repository oee_repository.materializar_oee().
Consultado pela API (Fase 7) para respostas rapidas do dashboard.
"""

from __future__ import annotations

import datetime

from sqlalchemy import (
    BigInteger,
    DateTime,
    Double,
    ForeignKey,
    Identity,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from oee_textil.core.database import Base


class OeeAgregado(Base):
    """Agregacao de OEE por maquina x janela de tempo."""

    __tablename__ = "oee_agregado"

    id: Mapped[int] = mapped_column(
        Integer,
        Identity(),
        primary_key=True,
    )
    maquina_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("maquinas.maquina_id"),
    )
    janela_inicio: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
    )
    janela_fim: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
    )
    disponibilidade: Mapped[float] = mapped_column(Double)
    performance: Mapped[float] = mapped_column(Double)
    qualidade: Mapped[float] = mapped_column(Double)
    oee: Mapped[float] = mapped_column(Double)
    unidades_produzidas: Mapped[int | None] = mapped_column(
        BigInteger,
        nullable=True,
    )
    unidades_refugo: Mapped[int | None] = mapped_column(
        BigInteger,
        nullable=True,
    )
    tempo_planejado_s: Mapped[float | None] = mapped_column(
        Double,
        nullable=True,
    )
    tempo_rodando_s: Mapped[float | None] = mapped_column(
        Double,
        nullable=True,
    )
    ts_calculo: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    __table_args__ = (
        UniqueConstraint(
            "maquina_id",
            "janela_inicio",
            "janela_fim",
            name="uq_oee_agregado_maquina_janela",
        ),
    )

    def __repr__(self) -> str:
        return (
            f"OeeAgregado(maquina_id={self.maquina_id!r}, "
            f"janela={self.janela_inicio}..{self.janela_fim}, "
            f"oee={self.oee:.4f})"
        )
