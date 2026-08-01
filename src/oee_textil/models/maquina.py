"""Modelo ORM — Maquina (catalogo de maquinas do chao de fabrica).

Fonte de dados: data/exemplos-mqtt/maquinas.csv (seed via oee_textil.seed).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from oee_textil.core.database import Base

if TYPE_CHECKING:
    from oee_textil.models.estado import EstadoMaquina
    from oee_textil.models.parada import Parada
    from oee_textil.models.producao import Producao
    from oee_textil.models.telemetria import Telemetria


class Maquina(Base):
    """Catalogo de maquinas com hierarquia Galpao -> Linha -> Maquina."""

    __tablename__ = "maquinas"

    maquina_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    galpao: Mapped[str] = mapped_column(String(10))
    linha: Mapped[str] = mapped_column(String(10))
    tipo: Mapped[str] = mapped_column(String(30))
    tempo_ciclo_ideal_s: Mapped[float] = mapped_column()

    # Relationships (one-to-many)
    telemetrias: Mapped[list[Telemetria]] = relationship(
        back_populates="maquina",
    )
    estados: Mapped[list[EstadoMaquina]] = relationship(
        back_populates="maquina",
    )
    paradas: Mapped[list[Parada]] = relationship(
        back_populates="maquina",
    )
    producoes: Mapped[list[Producao]] = relationship(
        back_populates="maquina",
    )

    def __repr__(self) -> str:
        return (
            f"Maquina(maquina_id={self.maquina_id!r}, "
            f"galpao={self.galpao!r}, linha={self.linha!r})"
        )
