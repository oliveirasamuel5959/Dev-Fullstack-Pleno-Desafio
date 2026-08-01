"""Testes do consumidor MQTT — hash, resolucao, dead-letter, dedup."""

import json
from datetime import UTC, datetime

import pytest

from oee_textil.core.database import SessionLocal
from oee_textil.models.estado import EstadoMaquina
from oee_textil.models.parada import Parada
from oee_textil.models.producao import Producao
from oee_textil.models.telemetria import Telemetria
from oee_textil.services.consumidor import (
    calcular_content_hash,
    dead_letter,
    inserir_evento,
    inserir_telemetria,
    resolver_tabela,
)

# ---------------------------------------------------------------------------
# Hash
# ---------------------------------------------------------------------------


def test_calcular_hash_deterministico():
    """Mesmo input → mesmo hash."""
    dados = {
        "schema": "parada.v1",
        "maquina_id": "T1",
        "ts_sensor": "2026-03-10T13:45:00Z",
        "motivo_codigo": "QBR_AGULHA",
    }
    assert calcular_content_hash(dados) == calcular_content_hash(dados)


def test_calcular_hash_diferente_por_conteudo():
    """Inputs diferentes → hashes diferentes."""
    a = {"schema": "estado.v1", "maquina_id": "T1", "estado": "rodando"}
    b = {"schema": "estado.v1", "maquina_id": "T1", "estado": "parado"}
    assert calcular_content_hash(a) != calcular_content_hash(b)


def test_calcular_hash_ignora_ts_ingestao():
    """Mesmo payload com ts_ingestao diferente → mesmo hash."""
    a = {
        "schema": "parada.v1",
        "maquina_id": "T1",
        "ts_sensor": "2026-03-10T13:45:00Z",
        "ts_ingestao": "2026-03-10T13:45:01Z",
    }
    b = {
        "schema": "parada.v1",
        "maquina_id": "T1",
        "ts_sensor": "2026-03-10T13:45:00Z",
        "ts_ingestao": "2026-03-10T13:45:05Z",
    }
    assert calcular_content_hash(a) == calcular_content_hash(b)


def test_calcular_hash_ignora_id():
    """Mesmo payload com id diferente → mesmo hash."""
    a = {"schema": "parada.v1", "maquina_id": "T1", "id": 1, "planejada": True}
    b = {"schema": "parada.v1", "maquina_id": "T1", "id": 2, "planejada": True}
    assert calcular_content_hash(a) == calcular_content_hash(b)


# ---------------------------------------------------------------------------
# Resolver tabela
# ---------------------------------------------------------------------------


def test_resolver_tabela_telemetria():
    assert resolver_tabela("telemetria.v1") is Telemetria


def test_resolver_tabela_estado():
    assert resolver_tabela("estado.v1") is EstadoMaquina


def test_resolver_tabela_parada():
    assert resolver_tabela("parada.v1") is Parada


def test_resolver_tabela_producao():
    assert resolver_tabela("producao.v1") is Producao


def test_resolver_tabela_desconhecido():
    with pytest.raises(ValueError, match="Schema desconhecido"):
        resolver_tabela("inexistente.v9")


# ---------------------------------------------------------------------------
# Dead-letter
# ---------------------------------------------------------------------------


def test_dead_letter_escreve_arquivo(tmp_path):
    """Dead-letter deve escrever NDJSON valido."""
    dl_path = tmp_path / "dead-letter.ndjson"
    payload = {"schema": "telemetria.v1", "rpm": -1}
    erro = "rpm negativo"
    topico = "fabrica/G1/L2/T1/telemetria"

    dead_letter(payload, erro, topico, caminho=dl_path)

    assert dl_path.exists()
    linhas = dl_path.read_text(encoding="utf-8").strip().split("\n")
    assert len(linhas) == 1
    registro = json.loads(linhas[0])
    assert registro["payload"] == payload
    assert registro["erro"] == erro
    assert registro["topico"] == topico
    assert "ts_ingestao" in registro


def test_dead_letter_append(tmp_path):
    """Multiplas chamadas devem fazer append, nao sobrescrever."""
    dl_path = tmp_path / "dead-letter.ndjson"

    dead_letter({"a": 1}, "erro1", "t1", caminho=dl_path)
    dead_letter({"b": 2}, "erro2", "t2", caminho=dl_path)

    linhas = dl_path.read_text(encoding="utf-8").strip().split("\n")
    assert len(linhas) == 2


# ---------------------------------------------------------------------------
# Insercao com dedup (requer banco)
# ---------------------------------------------------------------------------


@pytest.mark.smoke
def test_inserir_telemetria_dedup():
    """Segunda insercao da mesma telemetria deve ser ignorada (PK natural)."""
    # Timestamp unico para nao conflitar com dados do simulador/consumidor
    ts = datetime(2099, 1, 1, 0, 0, 0, 0, tzinfo=UTC)
    dados = {
        "maquina_id": "TEAR-G1-L2-07",
        "ts_sensor": ts,
        "rpm": 118.4,
        "voltas_acumuladas": 90418223,
        "temperatura_c": 41.2,
        "vibracao_mm_s": 2.1,
    }

    # Limpar dados anteriores do mesmo timestamp (se existirem)
    with SessionLocal() as session:
        session.execute(
            Telemetria.__table__.delete().where(
                Telemetria.maquina_id == "TEAR-G1-L2-07",
                Telemetria.ts_sensor == ts,
            )
        )
        session.commit()

    # Primeira insercao
    ok1 = inserir_telemetria(dados)
    # Segunda insercao (mesma PK)
    ok2 = inserir_telemetria(dados)

    # Primeira deve inserir, segunda deve ser ignorada como duplicata
    assert ok1 is True
    assert ok2 is False
    # Limpar para nao poluir
    with SessionLocal() as session:
        session.execute(
            Telemetria.__table__.delete().where(
                Telemetria.maquina_id == "TEAR-G1-L2-07",
                Telemetria.ts_sensor == ts,
            )
        )
        session.commit()


@pytest.mark.smoke
def test_inserir_evento_dedup_hash():
    """Segunda insercao do mesmo evento deve ser ignorada (content_hash)."""
    # Timestamp unico para nao conflitar com dados do simulador/consumidor
    ts = datetime(2099, 1, 1, 0, 0, 0, 0, tzinfo=UTC)
    dados = {
        "maquina_id": "TEAR-G1-L2-07",
        "motivo_codigo": "QBR_AGULHA",
        "motivo_descricao": "Quebra de agulha",
        "planejada": False,
        "ts_sensor": ts,
    }

    # Limpar dados anteriores do mesmo timestamp (se existirem)
    with SessionLocal() as session:
        session.execute(
            Parada.__table__.delete().where(
                Parada.maquina_id == "TEAR-G1-L2-07",
                Parada.ts_sensor == ts,
            )
        )
        session.commit()

    ok1 = inserir_evento(Parada, dados)
    ok2 = inserir_evento(Parada, dados)

    # Primeira deve inserir, segunda deve ser ignorada como duplicata
    assert ok1 is True
    assert ok2 is False
    # Limpar
    with SessionLocal() as session:
        # Remove pelo content_hash (mais preciso que maquina_id sozinho)
        from oee_textil.services.consumidor import calcular_content_hash

        hash_val = calcular_content_hash(dados)
        session.execute(
            Parada.__table__.delete().where(Parada.content_hash == hash_val)
        )
        session.commit()


@pytest.mark.smoke
def test_duplicata_fixture_uma_row():
    """A duplicata intencional do fixture gera exatamente 1 row no banco."""
    dados_parada = {
        "maquina_id": "TEAR-G1-L2-07",
        "motivo_codigo": "QBR_AGULHA",
        "motivo_descricao": "Quebra de agulha",
        "planejada": False,
        "ts_sensor": datetime(2026, 3, 10, 13, 45, 0, tzinfo=UTC),
    }

    # Inserir 2x (simula a duplicata do fixture)
    inserir_evento(Parada, dados_parada)
    inserir_evento(Parada, dados_parada)

    # Contar rows
    with SessionLocal() as session:
        count = (
            session.query(Parada)
            .filter(
                Parada.maquina_id == "TEAR-G1-L2-07",
                Parada.motivo_codigo == "QBR_AGULHA",
            )
            .count()
        )

    assert count == 1, f"Esperado 1 row, encontrado {count}"

    # Limpar
    with SessionLocal() as session:
        session.execute(
            Parada.__table__.delete().where(Parada.maquina_id == "TEAR-G1-L2-07")
        )
        session.commit()
