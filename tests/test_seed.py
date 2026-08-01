"""Testes de integracao do seed de catalogo.

Requer banco TimescaleDB migrado e populado (make setup-db).
"""

import pytest
from sqlalchemy import create_engine, text

from oee_textil.core.config import get_database_url


@pytest.fixture
def db_url():
    """URL de conexao com o banco."""
    return get_database_url()


@pytest.mark.smoke
def test_maquinas_count(db_url):
    """Deve haver 4 maquinas apos o seed."""
    engine = create_engine(db_url)
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT count(*) FROM maquinas"))
            count = result.scalar()
            assert count == 4, f"Esperado 4 maquinas, obtido {count}"
    finally:
        engine.dispose()


@pytest.mark.smoke
def test_motivos_parada_count(db_url):
    """Deve haver 7 motivos de parada apos o seed."""
    engine = create_engine(db_url)
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT count(*) FROM motivos_parada"))
            count = result.scalar()
            assert count == 7, f"Esperado 7 motivos, obtido {count}"
    finally:
        engine.dispose()


@pytest.mark.smoke
def test_turnos_count(db_url):
    """Deve haver 3 turnos apos o seed."""
    engine = create_engine(db_url)
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT count(*) FROM turnos"))
            count = result.scalar()
            assert count == 3, f"Esperado 3 turnos, obtido {count}"
    finally:
        engine.dispose()


@pytest.mark.smoke
def test_seed_idempotente(db_url):
    """Rodar seed 2x nao deve duplicar dados (ON CONFLICT DO NOTHING)."""
    from oee_textil.seed import main

    # Primeira execucao — conta o estado atual
    engine = create_engine(db_url)
    try:
        with engine.connect() as conn:
            count_antes = conn.execute(text("SELECT count(*) FROM maquinas")).scalar()
    finally:
        engine.dispose()

    # Executa seed novamente
    main([])

    # Conta depois
    engine2 = create_engine(db_url)
    try:
        with engine2.connect() as conn:
            count_depois = conn.execute(text("SELECT count(*) FROM maquinas")).scalar()
    finally:
        engine2.dispose()

    assert count_depois == count_antes, (
        f"Seed nao e idempotente: {count_antes} -> {count_depois}"
    )


@pytest.mark.smoke
def test_motivo_planejada_booleano(db_url):
    """Coluna planejada deve ser booleana, nao string."""
    engine = create_engine(db_url)
    try:
        with engine.connect() as conn:
            result = conn.execute(
                text(
                    "SELECT motivo_codigo, planejada FROM motivos_parada "
                    "WHERE motivo_codigo = 'SETUP'"
                )
            )
            row = result.fetchone()
            assert row is not None
            assert row[1] is True, f"SETUP.planejada deve ser True, obtido {row[1]}"
    finally:
        engine.dispose()
