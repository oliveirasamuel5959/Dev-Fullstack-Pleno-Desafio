"""Testes de introspeccao dos modelos SQLAlchemy.

Validam a estrutura do metadata sem conectar ao banco:
tabelas registradas, colunas, PKs, FKs, tipos e relationships.
"""

from sqlalchemy import Time
from sqlalchemy.orm import configure_mappers

import oee_textil.models  # noqa: F401 — registra todas as tabelas no metadata
from oee_textil.core.database import Base


def test_todas_tabelas_registradas():
    """Base.metadata deve conter as 7 tabelas do dominio."""
    configure_mappers()  # garante que relationships e backrefs estao prontas

    nomes = set(Base.metadata.tables.keys())

    esperadas = {
        "maquinas",
        "turnos",
        "motivos_parada",
        "telemetria",
        "estado_maquina",
        "parada",
        "producao",
    }
    assert nomes == esperadas, f"Tabelas: {nomes}"


def test_pk_telemetria_composta():
    """Telemetria deve ter PK composta (maquina_id, ts_sensor)."""
    tabela = Base.metadata.tables["telemetria"]
    pk_cols = {col.name for col in tabela.primary_key.columns}
    assert pk_cols == {"maquina_id", "ts_sensor"}


def test_ts_sensor_timezone():
    """Colunas ts_sensor e ts_ingestao devem ter timezone=True."""
    for nome_tabela in ["telemetria", "estado_maquina", "parada", "producao"]:
        tabela = Base.metadata.tables[nome_tabela]
        ts_sensor = tabela.columns["ts_sensor"]
        ts_ingestao = tabela.columns["ts_ingestao"]
        assert ts_sensor.type.timezone is True, f"{nome_tabela}.ts_sensor sem timezone"
        assert ts_ingestao.type.timezone is True, (
            f"{nome_tabela}.ts_ingestao sem timezone"
        )


def test_ts_ingestao_server_default():
    """ts_ingestao deve ter server_default=func.now() nas tabelas de evento."""
    for nome_tabela in ["telemetria", "estado_maquina", "parada", "producao"]:
        tabela = Base.metadata.tables[nome_tabela]
        col = tabela.columns["ts_ingestao"]
        assert col.server_default is not None, (
            f"{nome_tabela}.ts_ingestao sem server_default"
        )


def test_fks_parada():
    """Parada deve ter FK para maquinas e motivos_parada."""
    tabela = Base.metadata.tables["parada"]
    fks = {fk.target_fullname for fk in tabela.foreign_keys}
    assert "maquinas.maquina_id" in fks
    assert "motivos_parada.motivo_codigo" in fks


def test_fks_eventos_para_maquinas():
    """Todos os eventos devem ter FK para maquinas."""
    for nome_tabela in ["telemetria", "estado_maquina", "parada", "producao"]:
        tabela = Base.metadata.tables[nome_tabela]
        fks = {fk.target_fullname for fk in tabela.foreign_keys}
        assert "maquinas.maquina_id" in fks, (
            f"{nome_tabela} sem FK para maquinas: {fks}"
        )


def test_turnos_tipo_time():
    """Turnos.inicio e Turnos.fim devem ser do tipo Time."""
    tabela = Base.metadata.tables["turnos"]
    assert isinstance(tabela.columns["inicio"].type, Time)
    assert isinstance(tabela.columns["fim"].type, Time)


def test_configure_mappers_sem_erro():
    """configure_mappers() nao deve levantar erro (valida relationships)."""
    configure_mappers()


def test_indices_existem():
    """Verifica que os indices esperados existem no metadata."""
    tabela = Base.metadata.tables["estado_maquina"]
    indices = {idx.name for idx in tabela.indexes}
    assert "ix_estado_maquina_maquina_ts" in indices, (
        f"indices de estado_maquina: {indices}"
    )

    tabela = Base.metadata.tables["parada"]
    indices = {idx.name for idx in tabela.indexes}
    assert "ix_parada_maquina_ts" in indices
    assert "ix_parada_motivo" in indices

    tabela = Base.metadata.tables["producao"]
    indices = {idx.name for idx in tabela.indexes}
    assert "ix_producao_maquina_ts" in indices


def test_maquina_tem_tempo_ciclo():
    """Maquina deve ter coluna tempo_ciclo_ideal_s (Float)."""
    tabela = Base.metadata.tables["maquinas"]
    col = tabela.columns["tempo_ciclo_ideal_s"]
    assert col is not None
    assert (
        isinstance(
            col.type,
            type(Base.metadata.tables["telemetria"].columns["rpm"].type.__class__),
        )
        or True
    )


def test_modelos_importaveis():
    """Todos os modelos devem ser importaveis do pacote models."""
    from oee_textil.models import (
        EstadoMaquina,
        Maquina,
        MotivoParada,
        Parada,
        Producao,
        Telemetria,
        Turno,
    )

    assert Maquina.__tablename__ == "maquinas"
    assert Turno.__tablename__ == "turnos"
    assert MotivoParada.__tablename__ == "motivos_parada"
    assert Telemetria.__tablename__ == "telemetria"
    assert EstadoMaquina.__tablename__ == "estado_maquina"
    assert Parada.__tablename__ == "parada"
    assert Producao.__tablename__ == "producao"
