"""Testes de integracao das migracoes Alembic.

Requer banco TimescaleDB migrado (make migrate).
"""

import pytest
from sqlalchemy import text

from oee_textil.core.config import get_database_url


@pytest.fixture
def db_url():
    """URL de conexao com o banco (respeita env var)."""
    return get_database_url()


@pytest.mark.smoke
def test_alembic_version_existe(db_url):
    """Tabela alembic_version deve existir apos migrate."""
    from sqlalchemy import create_engine, inspect

    engine = create_engine(db_url)
    try:
        insp = inspect(engine)
        tabelas = insp.get_table_names()
        assert "alembic_version" in tabelas, f"Tabelas: {tabelas}"
    finally:
        engine.dispose()


@pytest.mark.smoke
def test_todas_tabelas_existem(db_url):
    """As 7 tabelas do dominio devem existir no banco apos migrate."""
    from sqlalchemy import create_engine, inspect

    engine = create_engine(db_url)
    try:
        insp = inspect(engine)
        tabelas = set(insp.get_table_names())

        esperadas = {
            "maquinas",
            "turnos",
            "motivos_parada",
            "telemetria",
            "estado_maquina",
            "parada",
            "producao",
            "alembic_version",
        }
        # Todas as esperadas devem estar presentes
        faltando = esperadas - tabelas
        assert not faltando, f"Tabelas faltando: {faltando}"
    finally:
        engine.dispose()


@pytest.mark.smoke
def test_telemetria_e_hypertable(db_url):
    """Telemetria deve estar registrada como hypertable TimescaleDB."""
    from sqlalchemy import create_engine

    engine = create_engine(db_url)
    try:
        with engine.connect() as conn:
            result = conn.execute(
                text(
                    "SELECT hypertable_name "
                    "FROM timescaledb_information.hypertables "
                    "WHERE hypertable_name = 'telemetria'"
                )
            )
            row = result.fetchone()
            assert row is not None, "telemetria nao e hypertable"
            assert row[0] == "telemetria"
    finally:
        engine.dispose()
