"""Repository OEE — consulta eventos brutos e alimenta funcoes puras.

Camada de acesso a dados para calculo de OEE. Consulta as tabelas de
producao, parada e maquinas para extrair os agregados necessarios e
chama as funcoes puras de oee_textil.services.oee.

Uso:
    from oee_textil.repositories.oee_repository import calcular_oee_maquina
    resultado = calcular_oee_maquina(session, "TEAR-G1-L2-07", inicio, fim)
"""

import datetime
from typing import Any

from sqlalchemy import func
from sqlalchemy.dialects.postgresql import insert as pg_insert

from oee_textil.models.maquina import Maquina
from oee_textil.models.oee_agregado import OeeAgregado
from oee_textil.models.parada import Parada
from oee_textil.models.producao import Producao
from oee_textil.services.oee import disponibilidade, oee, performance, qualidade


def buscar_ciclo_ideal(session: Any, maquina_id: str) -> float:
    """Busca o tempo de ciclo ideal da maquina no catalogo.

    Returns:
        tempo_ciclo_ideal_s. Levanta ValueError se maquina nao existe.
    """
    maquina = session.get(Maquina, maquina_id)
    if maquina is None:
        raise ValueError(f"Maquina nao encontrada no catalogo: {maquina_id}")
    return float(maquina.tempo_ciclo_ideal_s)


def buscar_tempo_planejado(
    session: Any,
    maquina_id: str,
    inicio: datetime.datetime,
    fim: datetime.datetime,
) -> float:
    """Calcula Tempo Planejado = duracao da janela - paradas planejadas.

    Returns:
        Tempo planejado em segundos.
    """
    duracao_janela_s = (fim - inicio).total_seconds()

    # Soma das paradas planejadas no periodo
    paradas_planejadas = (
        session.query(
            func.coalesce(
                func.sum(
                    func.extract("epoch", Parada.ts_sensor)
                    * 0  # placeholder — paradas nao tem duracao
                ),
                0,
            )
        )
        .filter(
            Parada.maquina_id == maquina_id,
            Parada.ts_sensor >= inicio,
            Parada.ts_sensor < fim,
            Parada.planejada.is_(True),
        )
        .scalar()
    )

    # TODO: paradas nao tem campo de duracao no modelo atual.
    # Por enquanto, Tempo Planejado = duracao da janela.
    # Quando o modelo de paradas incluir duracao, subtrair paradas_planejadas.
    # Issue: a duracao de uma parada e inferida do proximo evento de estado
    # (rodando apos parado). Isso e complexo e sera tratado em iteracao futura.
    _ = paradas_planejadas  # reservado para uso futuro

    return duracao_janela_s


def buscar_tempo_rodando(
    session: Any,
    maquina_id: str,
    inicio: datetime.datetime,
    fim: datetime.datetime,
) -> float:
    """Calcula Tempo Rodando = Tempo Planejado - paradas nao-planejadas.

    Returns:
        Tempo rodando em segundos.
    """
    tempo_planejado = buscar_tempo_planejado(session, maquina_id, inicio, fim)

    # Soma das paradas nao-planejadas no periodo
    paradas_nao_planejadas_count = (
        session.query(func.count(Parada.id))
        .filter(
            Parada.maquina_id == maquina_id,
            Parada.ts_sensor >= inicio,
            Parada.ts_sensor < fim,
            Parada.planejada.is_(False),
        )
        .scalar()
    )

    # TODO: cada parada nao-planejada precisa de uma estimativa de duracao.
    # Por enquanto, usamos um valor nominal de 5min por parada como placeholder.
    # Isso sera refinado quando o modelo tiver duracao de parada.
    duracao_estimada_por_parada_s = 300.0  # 5 min
    tempo_parado_nao_planejado = (
        paradas_nao_planejadas_count * duracao_estimada_por_parada_s
    )

    tempo_rodando = tempo_planejado - float(tempo_parado_nao_planejado)
    return max(0.0, tempo_rodando)


def buscar_producao(
    session: Any,
    maquina_id: str,
    inicio: datetime.datetime,
    fim: datetime.datetime,
) -> tuple[int, int]:
    """Busca total produzido e refugo no periodo.

    Returns:
        (unidades_produzidas, unidades_refugo).
    """
    resultado = (
        session.query(
            func.coalesce(func.sum(Producao.unidades_produzidas), 0),
            func.coalesce(func.sum(Producao.unidades_refugo), 0),
        )
        .filter(
            Producao.maquina_id == maquina_id,
            Producao.ts_sensor >= inicio,
            Producao.ts_sensor < fim,
        )
        .one()
    )

    return int(resultado[0]), int(resultado[1])


def calcular_oee_maquina(
    session: Any,
    maquina_id: str,
    inicio: datetime.datetime,
    fim: datetime.datetime,
) -> dict[str, Any]:
    """Calcula D/P/Q/OEE para uma maquina em uma janela.

    Returns:
        Dict com chaves: maquina_id, janela_inicio, janela_fim,
        disponibilidade, performance, qualidade, oee,
        unidades_produzidas, unidades_refugo,
        tempo_planejado_s, tempo_rodando_s.
    """
    ciclo_ideal = buscar_ciclo_ideal(session, maquina_id)
    tempo_planejado = buscar_tempo_planejado(session, maquina_id, inicio, fim)
    tempo_rodando = buscar_tempo_rodando(session, maquina_id, inicio, fim)
    total_produzido, total_refugo = buscar_producao(
        session,
        maquina_id,
        inicio,
        fim,
    )

    d = disponibilidade(tempo_rodando, tempo_planejado)
    p = performance(ciclo_ideal, total_produzido, tempo_rodando)
    q = qualidade(total_produzido, total_refugo)
    oee_valor = oee(d, p, q)

    return {
        "maquina_id": maquina_id,
        "janela_inicio": inicio,
        "janela_fim": fim,
        "disponibilidade": d,
        "performance": p,
        "qualidade": q,
        "oee": oee_valor,
        "unidades_produzidas": total_produzido,
        "unidades_refugo": total_refugo,
        "tempo_planejado_s": tempo_planejado,
        "tempo_rodando_s": tempo_rodando,
    }


def materializar_oee(
    session: Any,
    maquina_id: str,
    inicio: datetime.datetime,
    fim: datetime.datetime,
) -> bool:
    """Calcula OEE e persiste na tabela oee_agregado (upsert).

    Returns:
        True se inseriu, False se atualizou ou duplicata.
    """
    resultado = calcular_oee_maquina(session, maquina_id, inicio, fim)

    stmt = (
        pg_insert(OeeAgregado)
        .values(**resultado)
        .on_conflict_do_update(
            constraint="uq_oee_agregado_maquina_janela",
            set_={
                "disponibilidade": resultado["disponibilidade"],
                "performance": resultado["performance"],
                "qualidade": resultado["qualidade"],
                "oee": resultado["oee"],
                "unidades_produzidas": resultado["unidades_produzidas"],
                "unidades_refugo": resultado["unidades_refugo"],
                "tempo_planejado_s": resultado["tempo_planejado_s"],
                "tempo_rodando_s": resultado["tempo_rodando_s"],
                "ts_calculo": func.now(),
            },
        )
    )

    result = session.execute(stmt)
    session.commit()
    return result.rowcount > 0  # type: ignore[no-any-return]
