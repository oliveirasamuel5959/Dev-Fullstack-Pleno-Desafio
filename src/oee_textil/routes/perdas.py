"""Router de perdas — analise D/P/Q."""

import datetime
from typing import Any

from fastapi import APIRouter, Depends, Query

from oee_textil.repositories.oee_repository import calcular_oee_maquina
from oee_textil.routes.app import get_db
from oee_textil.schemas.api import FatoresOee, PerdasResponse

router = APIRouter(prefix="/api/v1/perdas", tags=["Perdas"])


@router.get("", response_model=PerdasResponse)
async def perdas(
    maquina_id: str = Query(...),
    inicio: datetime.datetime | None = Query(None),
    fim: datetime.datetime | None = Query(None),
    db: Any = Depends(get_db),
) -> PerdasResponse:
    """Analise de perdas D/P/Q para uma maquina no periodo."""
    if inicio is None:
        inicio = datetime.datetime.now(datetime.UTC) - datetime.timedelta(hours=8)
    if fim is None:
        fim = datetime.datetime.now(datetime.UTC)

    resultado = calcular_oee_maquina(db, maquina_id, inicio, fim)

    d = resultado["disponibilidade"]
    p = resultado["performance"]
    q = resultado["qualidade"]

    # Identificar maior perda
    perdas_map = {
        "Disponibilidade": 1.0 - d,
        "Performance": 1.0 - p,
        "Qualidade": 1.0 - q,
    }
    maior = max(perdas_map.keys(), key=lambda k: perdas_map[k])

    return PerdasResponse(
        maquina_id=maquina_id,
        fatores=FatoresOee(disponibilidade=d, performance=p, qualidade=q),
        maior_perda=maior,
        perda_percentual=round(perdas_map[maior] * 100, 2),
    )
