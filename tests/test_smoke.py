"""Smoke tests: verificam que o pacote e importavel e que a infraestrutura
externa (Mosquitto, TimescaleDB) esta acessivel.

Fase 0: importabilidade do pacote + entry point.
Fase 2: conectividade real com broker MQTT e banco de dados.
"""

import subprocess
import sys
import time

import paho.mqtt.client as mqtt
import pytest
from sqlalchemy import create_engine, text

# ---------------------------------------------------------------------------
# Fase 0 — Smoke do pacote
# ---------------------------------------------------------------------------


def test_pacote_raiz_importavel() -> None:
    """O pacote oee_textil deve ser importavel."""
    import oee_textil

    assert oee_textil.__doc__ is not None


def test_subpacotes_importaveis() -> None:
    """Todos os subpacotes definidos no layout devem ser importaveis."""
    subpacotes = [
        "oee_textil.core",
        "oee_textil.models",
        "oee_textil.schemas",
        "oee_textil.repositories",
        "oee_textil.services",
        "oee_textil.routes",
        "oee_textil.simulador",
    ]
    for nome in subpacotes:
        mod = __import__(nome, fromlist=["__doc__"])
        assert mod.__doc__ is not None, (
            f"Subpacote {nome} nao tem docstring de proposito"
        )


def test_entry_point_executa() -> None:
    """python -m oee_textil deve executar sem erro."""
    result = subprocess.run(
        [sys.executable, "-m", "oee_textil"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"Entry point falhou com stderr: {result.stderr}"
    assert "Hello from dev-fullstack-pleno-desafio!" in result.stdout


# ---------------------------------------------------------------------------
# Fase 2 — Smoke de infraestrutura (Mosquitto + TimescaleDB)
# ---------------------------------------------------------------------------


@pytest.mark.smoke
def test_mosquitto_connect() -> None:
    """Conecta ao Mosquitto, faz subscribe, publica e verifica recebimento."""
    broker_host = "localhost"
    broker_port = 1883
    topic = "smoke/test/mosquitto"
    payload = "ok"

    received: list[str] = []

    def on_message(
        client: mqtt.Client, userdata: object, msg: mqtt.MQTTMessage
    ) -> None:
        received.append(msg.payload.decode())

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_message = on_message

    client.connect(broker_host, broker_port)
    client.subscribe(topic)
    client.loop_start()

    try:
        client.publish(topic, payload)

        # Aguarda ate 5s pela mensagem
        deadline = time.monotonic() + 5
        while not received and time.monotonic() < deadline:
            time.sleep(0.1)

        assert received, "Nenhuma mensagem recebida do Mosquitto em 5s"
        assert received[0] == payload, (
            f"Payload esperado '{payload}', recebido '{received[0]}'"
        )
    finally:
        client.loop_stop()
        client.disconnect()


@pytest.mark.smoke
def test_timescaledb_connect() -> None:
    """Conecta ao TimescaleDB via SQLAlchemy e executa SELECT 1."""
    db_url = "postgresql://oee:oee_dev@localhost:5432/oee_textil"
    engine = create_engine(db_url)

    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            row = result.fetchone()
            assert row is not None, "SELECT 1 nao retornou resultado"
            assert row[0] == 1, f"Esperado 1, retornou {row[0]}"
    finally:
        engine.dispose()


@pytest.mark.smoke
def test_timescaledb_extension() -> None:
    """Verifica que a extensao TimescaleDB esta habilitada."""
    db_url = "postgresql://oee:oee_dev@localhost:5432/oee_textil"
    engine = create_engine(db_url)

    try:
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT extname FROM pg_extension WHERE extname = 'timescaledb'")
            )
            row = result.fetchone()
            assert row is not None, "Extensao timescaledb nao encontrada"
            assert row[0] == "timescaledb"
    finally:
        engine.dispose()
