"""Router de paradas — Pareto de motivos."""

import datetime
from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func

from oee_textil.models.parada import Parada
from oee_textil.routes.app import get_db
from oee_textil.schemas.api import ParetoItem, ParetoResponse

router = APIRouter(prefix="/api/v1/paradas", tags=["Paradas"])


@router.get("/pareto", response_model=ParetoResponse)
async def pareto_paradas(
    inicio: datetime.datetime | None = Query(None),
    fim: datetime.datetime | None = Query(None),
    db: Any = Depends(get_db),
) -> ParetoResponse:
    """Pareto de motivos de parada no periodo (ordenado por ocorrencias)."""
    if inicio is None:
        inicio = datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=7)
    if fim is None:
        fim = datetime.datetime.now(datetime.UTC)

    rows = (
        db.query(
            Parada.motivo_codigo,
            Parada.motivo_descricao,
            func.count(Parada.id).label("ocorrencias"),
            Parada.planejada,
        )
        .filter(
            Parada.ts_sensor >= inicio,
            Parada.ts_sensor < fim,
        )
        .group_by(
            Parada.motivo_codigo,
            Parada.motivo_descricao,
            Parada.planejada,
        )
        .order_by(func.count(Parada.id).desc())
        .all()
    )

    return ParetoResponse(
        items=[
            ParetoItem(
                motivo_codigo=row.motivo_codigo,
                motivo_descricao=row.motivo_descricao,
                ocorrencias=row.ocorrencias,
                planejada=row.planejada,
            )
            for row in rows
        ],
        periodo_inicio=inicio,
        periodo_fim=fim,
    )
