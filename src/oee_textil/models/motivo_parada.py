"""Modelo ORM — MotivoParada (catalogo de motivos de parada).

Fonte de dados: data/exemplos-mqtt/motivos-parada.csv (seed via oee_textil.seed).
O campo planejada define se a parada desconta Disponibilidade (mission §4.3).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from oee_textil.core.database import Base

if TYPE_CHECKING:
    from oee_textil.models.parada import Parada


class MotivoParada(Base):
    """Catalogo de motivos de parada com classificacao planejada/nao-planejada."""

    __tablename__ = "motivos_parada"

    motivo_codigo: Mapped[str] = mapped_column(String(30), primary_key=True)
    descricao: Mapped[str] = mapped_column(String(100))
    planejada: Mapped[bool] = mapped_column(Boolean)

    # Relationships
    paradas: Mapped[list[Parada]] = relationship(
        back_populates="motivo",
    )

    def __repr__(self) -> str:
        return (
            f"MotivoParada(motivo_codigo={self.motivo_codigo!r}, "
            f"planejada={self.planejada})"
        )
