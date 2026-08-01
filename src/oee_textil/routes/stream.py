"""Router de streaming SSE — estado e OEE em tempo real.

GET /api/v1/stream — Server-Sent Events a cada 2s.
"""

import asyncio
import datetime
import json
from collections.abc import AsyncGenerator

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from sqlalchemy import func

from oee_textil.core.database import SessionLocal
from oee_textil.models.estado import EstadoMaquina
from oee_textil.models.maquina import Maquina
from oee_textil.repositories.oee_repository import calcular_oee_maquina

router = APIRouter(prefix="/api/v1", tags=["Stream"])


async def _gerar_eventos(request: Request) -> AsyncGenerator[str]:
    """Generator SSE: envia estado + OEE a cada 2s.

    Mostra TODAS as maquinas do catalogo (nao so as que tem eventos).
    Calcula OEE on-the-fly (nao depende de oee_agregado pre-preenchido).
    """
    while True:
        if await request.is_disconnected():
            break

        session = SessionLocal()
        try:
            # Buscar catalogo completo
            maquinas = session.query(Maquina).all()

            # Ultimo estado de cada maquina (pode ser None)
            subq = (
                session.query(
                    EstadoMaquina.maquina_id,
                    func.max(EstadoMaquina.ts_sensor).label("max_ts"),
                )
                .group_by(EstadoMaquina.maquina_id)
                .subquery()
            )

            rows = (
                session.query(
                    EstadoMaquina.maquina_id,
                    EstadoMaquina.estado,
                )
                .join(
                    subq,
                    (EstadoMaquina.maquina_id == subq.c.maquina_id)
                    & (EstadoMaquina.ts_sensor == subq.c.max_ts),
                )
                .all()
            )
            ultimos_estados: dict[str, str] = {
                row.maquina_id: row.estado for row in rows
            }

            # Construir lista de estados (todas as maquinas)
            estados = []
            for m in maquinas:
                estado = ultimos_estados.get(m.maquina_id, "desconhecido")
                estados.append(
                    {
                        "maquina_id": m.maquina_id,
                        "galpao": m.galpao,
                        "linha": m.linha,
                        "tipo": m.tipo,
                        "estado": estado,
                    }
                )

            # OEE on-the-fly para cada maquina (turno atual)
            agora = datetime.datetime.now(datetime.UTC)
            hora = agora.hour
            if 6 <= hora < 14:
                inicio = agora.replace(hour=6, minute=0, second=0, microsecond=0)
                fim = agora.replace(hour=14, minute=0, second=0, microsecond=0)
            elif 14 <= hora < 22:
                inicio = agora.replace(hour=14, minute=0, second=0, microsecond=0)
                fim = agora.replace(hour=22, minute=0, second=0, microsecond=0)
            elif hora >= 22:
                inicio = agora.replace(hour=22, minute=0, second=0, microsecond=0)
                fim = inicio + datetime.timedelta(hours=8)
            else:
                inicio = (agora - datetime.timedelta(days=1)).replace(
                    hour=22,
                    minute=0,
                    second=0,
                    microsecond=0,
                )
                fim = inicio + datetime.timedelta(hours=8)

            oee_list = []
            for m in maquinas:
                try:
                    r = calcular_oee_maquina(session, m.maquina_id, inicio, fim)
                    oee_list.append(
                        {
                            "maquina_id": r["maquina_id"],
                            "oee": round(r["oee"], 4),
                            "disponibilidade": round(r["disponibilidade"], 4),
                            "performance": round(r["performance"], 4),
                            "qualidade": round(r["qualidade"], 4),
                        }
                    )
                except ValueError:
                    continue

            data = {"estados": estados, "oee": oee_list}
            yield f"data: {json.dumps(data)}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'erro': str(e)})}\n\n"
        finally:
            session.close()

        await asyncio.sleep(2)


@router.get("/stream")
async def stream(request: Request) -> StreamingResponse:
    """SSE: estado das maquinas + OEE em tempo real (2s)."""
    return StreamingResponse(
        _gerar_eventos(request),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
