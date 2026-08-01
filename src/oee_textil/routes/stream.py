"""Router de streaming SSE — estado e OEE em tempo real.

GET /api/v1/stream — Server-Sent Events a cada 2s.
"""

import asyncio
import json
from typing import Any

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from sqlalchemy import func

from oee_textil.models.estado import EstadoMaquina
from oee_textil.models.maquina import Maquina
from oee_textil.models.oee_agregado import OeeAgregado
from oee_textil.routes.app import get_db

router = APIRouter(prefix="/api/v1", tags=["Stream"])


async def _gerar_eventos(db: Any, request: Request) -> Any:
    """Generator SSE: envia estado + OEE a cada 2s."""
    while True:
        if await request.is_disconnected():
            break

        try:
            # Ultimo estado de cada maquina
            subq = (
                db.query(
                    EstadoMaquina.maquina_id,
                    func.max(EstadoMaquina.ts_sensor).label("max_ts"),
                )
                .group_by(EstadoMaquina.maquina_id)
                .subquery()
            )

            estados = (
                db.query(
                    Maquina.maquina_id,
                    Maquina.galpao,
                    Maquina.linha,
                    Maquina.tipo,
                    EstadoMaquina.estado,
                )
                .join(subq, Maquina.maquina_id == subq.c.maquina_id)
                .join(
                    EstadoMaquina,
                    (EstadoMaquina.maquina_id == subq.c.maquina_id)
                    & (EstadoMaquina.ts_sensor == subq.c.max_ts),
                )
                .all()
            )

            # Ultimo OEE agregado
            oee_rows = (
                db.query(OeeAgregado)
                .order_by(OeeAgregado.ts_calculo.desc())
                .limit(4)
                .all()
            )

            data = {
                "estados": [
                    {
                        "maquina_id": e.maquina_id,
                        "galpao": e.galpao,
                        "linha": e.linha,
                        "tipo": e.tipo,
                        "estado": e.estado,
                    }
                    for e in estados
                ],
                "oee": [
                    {
                        "maquina_id": o.maquina_id,
                        "oee": round(o.oee, 4),
                        "disponibilidade": round(o.disponibilidade, 4),
                        "performance": round(o.performance, 4),
                        "qualidade": round(o.qualidade, 4),
                    }
                    for o in oee_rows
                ],
            }

            yield f"data: {json.dumps(data)}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'erro': str(e)})}\n\n"

        await asyncio.sleep(2)


@router.get("/stream")
async def stream(request: Request, db: Any = Depends(get_db)) -> StreamingResponse:
    """SSE: estado das maquinas + OEE em tempo real (2s)."""
    return StreamingResponse(
        _gerar_eventos(db, request),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
