"""Router de estado — maquinas paradas/anomalas agora."""

from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy import func

from oee_textil.models.estado import EstadoMaquina
from oee_textil.models.maquina import Maquina
from oee_textil.routes.app import get_db
from oee_textil.schemas.api import EstadoItem, EstadoResponse

router = APIRouter(prefix="/api/v1/estado", tags=["Estado"])


@router.get("/atual", response_model=EstadoResponse)
async def estado_atual(
    db: Any = Depends(get_db),
) -> EstadoResponse:
    """Estado atual de todas as maquinas (ultimo evento de estado conhecido)."""
    # Subquery: ultimo estado de cada maquina
    subq = (
        db.query(
            EstadoMaquina.maquina_id,
            func.max(EstadoMaquina.ts_sensor).label("max_ts"),
        )
        .group_by(EstadoMaquina.maquina_id)
        .subquery()
    )

    rows = (
        db.query(
            Maquina.maquina_id,
            Maquina.galpao,
            Maquina.linha,
            Maquina.tipo,
            EstadoMaquina.estado,
            EstadoMaquina.ts_sensor,
        )
        .join(subq, Maquina.maquina_id == subq.c.maquina_id)
        .join(
            EstadoMaquina,
            (EstadoMaquina.maquina_id == subq.c.maquina_id)
            & (EstadoMaquina.ts_sensor == subq.c.max_ts),
        )
        .all()
    )

    items = [
        EstadoItem(
            maquina_id=row.maquina_id,
            galpao=row.galpao,
            linha=row.linha,
            tipo=row.tipo,
            estado=row.estado,
            ts_ultimo_evento=row.ts_sensor,
        )
        for row in rows
    ]

    rodando = sum(1 for i in items if i.estado == "rodando")
    parado = len(items) - rodando

    return EstadoResponse(
        maquinas=items,
        total=len(items),
        rodando=rodando,
        parado=parado,
    )
