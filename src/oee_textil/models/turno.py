"""Modelo ORM — Turno (referencia fixa de 3 turnos de 8h).

Turnos: Manha 06h-14h, Tarde 14h-22h, Noite 22h-06h.
O turno da Noite cruza meia-noite — a instancia pertence a data do seu inicio
(22:00 do dia D = turno Noite de D). O calculo de Disponibilidade (Fase 6)
precisa tratar essa borda.

TODO: calendario de producao derivavel (ex.: gerar entradas por dia x turno
a partir dos turnos fixos). Fase 6 consome.
"""

from datetime import time

from sqlalchemy import String, Time
from sqlalchemy.orm import Mapped, mapped_column

from oee_textil.core.database import Base


class Turno(Base):
    """Turno de producao — referencia fixa, sem relationships nesta fase."""

    __tablename__ = "turnos"

    turno_id: Mapped[str] = mapped_column(String(10), primary_key=True)
    nome: Mapped[str] = mapped_column(String(30))
    inicio: Mapped[time] = mapped_column(Time)
    fim: Mapped[time] = mapped_column(Time)

    def __repr__(self) -> str:
        return (
            f"Turno(turno_id={self.turno_id!r}, nome={self.nome!r}, "
            f"inicio={self.inicio}, fim={self.fim})"
        )
