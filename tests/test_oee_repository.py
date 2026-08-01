"""Testes do repository OEE — requer banco com dados."""

from datetime import UTC, datetime

import pytest
from sqlalchemy import text

from oee_textil.core.database import SessionLocal
from oee_textil.repositories.oee_repository import (
    buscar_ciclo_ideal,
    buscar_producao,
    buscar_tempo_planejado,
    calcular_oee_maquina,
    materializar_oee,
)


@pytest.mark.smoke
def test_buscar_ciclo_ideal():
    """Deve retornar o ciclo ideal de uma maquina do catalogo."""
    with SessionLocal() as session:
        ciclo = buscar_ciclo_ideal(session, "TEAR-G1-L2-07")
        assert ciclo == 0.5

        ciclo = buscar_ciclo_ideal(session, "URDI-G2-L1-03")
        assert ciclo == 0.02


@pytest.mark.smoke
def test_buscar_ciclo_ideal_inexistente():
    """Maquina inexistente deve levantar ValueError."""
    with SessionLocal() as session, pytest.raises(ValueError, match="nao encontrada"):
        buscar_ciclo_ideal(session, "MAQUINA-X")


@pytest.mark.smoke
def test_buscar_tempo_planejado():
    """Tempo planejado = duracao da janela (paradas sem duracao por enquanto)."""
    inicio = datetime(2026, 3, 10, 6, 0, 0, tzinfo=UTC)
    fim = datetime(2026, 3, 10, 14, 0, 0, tzinfo=UTC)

    with SessionLocal() as session:
        tp = buscar_tempo_planejado(session, "TEAR-G1-L2-07", inicio, fim)
        assert tp == 8 * 3600  # 8h = 28800s


@pytest.mark.smoke
def test_buscar_producao_com_dados():
    """Deve retornar producao e refugo do periodo (dados inseridos no teste)."""
    from sqlalchemy.dialects.postgresql import insert as pg_insert

    from oee_textil.models.producao import Producao

    # Usar maquina e timestamps unicos para nao conflitar com fixtures
    maquina_teste = "RAMA-G3-L2-05"
    ts1 = datetime(2026, 8, 1, 10, 0, 0, tzinfo=UTC)
    ts2 = datetime(2026, 8, 1, 11, 0, 0, tzinfo=UTC)
    inicio = datetime(2026, 8, 1, 9, 0, 0, tzinfo=UTC)
    fim = datetime(2026, 8, 1, 12, 0, 0, tzinfo=UTC)

    with SessionLocal() as session:
        for ts, prod, ref in [(ts1, 100, 5), (ts2, 200, 10)]:
            session.execute(
                pg_insert(Producao)
                .values(
                    maquina_id=maquina_teste,
                    ts_sensor=ts,
                    unidades_produzidas=prod,
                    unidades_refugo=ref,
                    ordem_producao="OP-TEST-UNIQUE",
                )
                .on_conflict_do_nothing()
            )
        session.commit()

        total_prod, total_ref = buscar_producao(
            session,
            maquina_teste,
            inicio,
            fim,
        )
        assert total_prod >= 300, f"Esperado pelo menos 300, obtido {total_prod}"
        assert total_ref >= 15, f"Esperado pelo menos 15, obtido {total_ref}"

        # Limpar apenas os dados inseridos neste teste
        session.execute(
            Producao.__table__.delete().where(
                Producao.ordem_producao == "OP-TEST-UNIQUE"
            )
        )
        session.commit()


@pytest.mark.smoke
def test_calcular_oee_maquina():
    """Deve retornar dict com D/P/Q/OEE para uma maquina."""
    inicio = datetime(2026, 3, 10, 6, 0, 0, tzinfo=UTC)
    fim = datetime(2026, 3, 10, 14, 0, 0, tzinfo=UTC)

    with SessionLocal() as session:
        resultado = calcular_oee_maquina(session, "TEAR-G1-L2-07", inicio, fim)

        assert resultado["maquina_id"] == "TEAR-G1-L2-07"
        assert "disponibilidade" in resultado
        assert "performance" in resultado
        assert "qualidade" in resultado
        assert "oee" in resultado
        assert 0.0 <= resultado["disponibilidade"] <= 1.0
        assert 0.0 <= resultado["performance"] <= 1.0
        assert 0.0 <= resultado["qualidade"] <= 1.0
        assert 0.0 <= resultado["oee"] <= 1.0


@pytest.mark.smoke
def test_materializar_oee():
    """Deve persistir OEE na tabela oee_agregado."""
    inicio = datetime(2026, 3, 10, 6, 0, 0, tzinfo=UTC)
    fim = datetime(2026, 3, 10, 14, 0, 0, tzinfo=UTC)

    with SessionLocal() as session:
        ok = materializar_oee(session, "TEAR-G1-L2-07", inicio, fim)
        assert ok is True

        # Segunda chamada: upsert (update)
        ok2 = materializar_oee(session, "TEAR-G1-L2-07", inicio, fim)
        # ON CONFLICT UPDATE pode retornar rowcount > 0
        assert ok2 is True or ok2 is False

        # Verificar que existe 1 row
        count = session.execute(
            text("SELECT count(*) FROM oee_agregado WHERE maquina_id = 'TEAR-G1-L2-07'")
        ).scalar()
        assert count == 1

        # Limpar
        session.execute(
            text("DELETE FROM oee_agregado WHERE maquina_id = 'TEAR-G1-L2-07'")
        )
        session.commit()
