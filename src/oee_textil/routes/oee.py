"""Router de OEE — endpoints de consulta ao indicador."""

import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query

from oee_textil.models.maquina import Maquina
from oee_textil.models.oee_agregado import OeeAgregado
from oee_textil.repositories.oee_repository import calcular_oee_maquina
from oee_textil.routes.app import get_db
from oee_textil.schemas.api import (
    FatoresOee,
    OeeResponse,
    OeeSerieItem,
)

router = APIRouter(prefix="/api/v1/oee", tags=["OEE"])


@router.get("/atual", response_model=list[OeeResponse])
async def oee_atual(
    maquina_id: str | None = Query(None),
    galpao: str | None = Query(None),
    linha: str | None = Query(None),
    db: Any = Depends(get_db),
) -> list[OeeResponse]:
    """OEE atual por maquina, galpao ou linha.

    Sem parametros: retorna OEE de todas as maquinas no turno atual.
    """
    # Janela default: turno atual
    agora = datetime.datetime.now(datetime.UTC)
    hora = agora.hour
    if 6 <= hora < 14:
        inicio = agora.replace(hour=6, minute=0, second=0, microsecond=0)
        fim = agora.replace(hour=14, minute=0, second=0, microsecond=0)
    elif 14 <= hora < 22:
        inicio = agora.replace(hour=14, minute=0, second=0, microsecond=0)
        fim = agora.replace(hour=22, minute=0, second=0, microsecond=0)
    else:
        if hora >= 22:
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

    # Se maquina_id especifico, calcula on-the-fly
    if maquina_id:
        try:
            resultado = calcular_oee_maquina(db, maquina_id, inicio, fim)
        except ValueError as e:
            raise HTTPException(404, str(e)) from e
        return [
            OeeResponse(
                maquina_id=maquina_id,
                janela_inicio=inicio,
                janela_fim=fim,
                fatores=FatoresOee(
                    disponibilidade=resultado["disponibilidade"],
                    performance=resultado["performance"],
                    qualidade=resultado["qualidade"],
                ),
                oee=resultado["oee"],
                unidades_produzidas=resultado["unidades_produzidas"],
                unidades_refugo=resultado["unidades_refugo"],
                tempo_planejado_s=resultado["tempo_planejado_s"],
                tempo_rodando_s=resultado["tempo_rodando_s"],
            )
        ]

    # Agregacao por galpao/linha: consulta oee_agregado
    query = db.query(OeeAgregado).filter(
        OeeAgregado.janela_inicio >= inicio,
        OeeAgregado.janela_inicio < fim,
    )

    if galpao:
        maquinas = (
            db.query(Maquina.maquina_id)
            .filter(
                Maquina.galpao == galpao,
            )
            .all()
        )
        ids = [m[0] for m in maquinas]
        if not ids:
            raise HTTPException(404, f"Galpao {galpao} nao encontrado")
        query = query.filter(OeeAgregado.maquina_id.in_(ids))

    if linha:
        maquinas = (
            db.query(Maquina.maquina_id)
            .filter(
                Maquina.linha == linha,
            )
            .all()
        )
        ids = [m[0] for m in maquinas]
        if not ids:
            raise HTTPException(404, f"Linha {linha} nao encontrada")
        query = query.filter(OeeAgregado.maquina_id.in_(ids))

    rows = query.all()

    if not rows:
        return []

    return [
        OeeResponse(
            maquina_id=row.maquina_id,
            janela_inicio=row.janela_inicio,
            janela_fim=row.janela_fim,
            fatores=FatoresOee(
                disponibilidade=row.disponibilidade,
                performance=row.performance,
                qualidade=row.qualidade,
            ),
            oee=row.oee,
            unidades_produzidas=row.unidades_produzidas,
            unidades_refugo=row.unidades_refugo,
            tempo_planejado_s=row.tempo_planejado_s,
            tempo_rodando_s=row.tempo_rodando_s,
        )
        for row in rows
    ]


@router.get("/serie", response_model=list[OeeSerieItem])
async def oee_serie(
    maquina_id: str = Query(...),
    inicio: datetime.datetime | None = Query(None),
    fim: datetime.datetime | None = Query(None),
    db: Any = Depends(get_db),
) -> list[OeeSerieItem]:
    """Serie temporal de OEE para uma maquina."""
    if inicio is None:
        inicio = datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=1)
    if fim is None:
        fim = datetime.datetime.now(datetime.UTC)

    rows = (
        db.query(OeeAgregado)
        .filter(
            OeeAgregado.maquina_id == maquina_id,
            OeeAgregado.janela_inicio >= inicio,
            OeeAgregado.janela_fim <= fim,
        )
        .order_by(OeeAgregado.janela_inicio)
        .all()
    )

    return [
        OeeSerieItem(
            maquina_id=row.maquina_id,
            janela_inicio=row.janela_inicio,
            janela_fim=row.janela_fim,
            oee=row.oee,
            disponibilidade=row.disponibilidade,
            performance=row.performance,
            qualidade=row.qualidade,
        )
        for row in rows
    ]
