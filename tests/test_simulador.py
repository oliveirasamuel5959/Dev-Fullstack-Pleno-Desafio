"""Testes de integracao do simulador MQTT.

Requer broker Mosquitto rodando em localhost:1883 (make up).
"""

import time

import paho.mqtt.client as mqtt
import pytest

from oee_textil.simulador.catalogo import carregar_catalogo
from oee_textil.simulador.cli import _parse_args
from oee_textil.simulador.leitor import carregar_mensagens
from oee_textil.simulador.publisher import _construir_topico, publicar_mensagens

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def catalogo():
    """Catalogo carregado dos fixtures reais."""
    return carregar_catalogo("data/exemplos-mqtt")


@pytest.fixture
def mensagens():
    """Mensagens carregadas dos fixtures reais."""
    return carregar_mensagens("data/exemplos-mqtt")


@pytest.fixture
def cliente_mqtt():
    """Cliente paho-mqtt conectado ao broker local."""
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.connect("localhost", 1883)
    yield client
    client.disconnect()


# ---------------------------------------------------------------------------
# Testes unitarios da CLI (sem broker)
# ---------------------------------------------------------------------------


def test_parse_args_defaults():
    """Sem argumentos, deve retornar os defaults."""
    args = _parse_args([])
    assert args.broker_host == "localhost"
    assert args.broker_port == 1883
    assert args.interval == 1.0
    assert args.speed == 1.0
    assert args.loop is False
    assert args.data_dir == "data/exemplos-mqtt"


def test_parse_args_custom():
    """Argumentos customizados devem ser parseados corretamente."""
    args = _parse_args(
        [
            "--broker-host",
            "10.0.0.1",
            "--broker-port",
            "1884",
            "--interval",
            "0.5",
            "--speed",
            "60",
            "--loop",
            "--data-dir",
            "/tmp/dados",
        ]
    )
    assert args.broker_host == "10.0.0.1"
    assert args.broker_port == 1884
    assert args.interval == 0.5
    assert args.speed == 60.0
    assert args.loop is True
    assert args.data_dir == "/tmp/dados"


# ---------------------------------------------------------------------------
# Testes de construcao de topico
# ---------------------------------------------------------------------------


def test_construir_topico_telemetria(catalogo):
    """Topico de telemetria deve seguir o formato esperado."""
    topico = _construir_topico("telemetria.v1", catalogo, "TEAR-G1-L2-07")
    assert topico == "fabrica/G1/L2/TEAR-G1-L2-07/telemetria"


def test_construir_topico_parada(catalogo):
    """Topico de parada deve seguir o formato esperado."""
    topico = _construir_topico("parada.v1", catalogo, "TEAR-G1-L2-07")
    assert topico == "fabrica/G1/L2/TEAR-G1-L2-07/parada"


def test_construir_topico_producao(catalogo):
    """Topico de producao deve seguir o formato esperado."""
    topico = _construir_topico("producao.v1", catalogo, "URDI-G2-L1-03")
    assert topico == "fabrica/G2/L1/URDI-G2-L1-03/producao"


def test_construir_topico_estado(catalogo):
    """Topico de estado deve seguir o formato esperado."""
    topico = _construir_topico("estado.v1", catalogo, "TEAR-G1-L2-07")
    assert topico == "fabrica/G1/L2/TEAR-G1-L2-07/estado"


def test_construir_topico_maquina_inexistente(catalogo):
    """Maquina fora do catalogo deve levantar KeyError."""
    with pytest.raises(KeyError):
        _construir_topico("telemetria.v1", catalogo, "MAQUINA-X")


# ---------------------------------------------------------------------------
# Testes de integracao (requer broker Mosquitto rodando)
# ---------------------------------------------------------------------------


@pytest.mark.smoke
def test_publicar_mensagens_integracao(cliente_mqtt, catalogo, mensagens):
    """Publica mensagens reais e verifica que chegam ao broker."""
    received: list[mqtt.MQTTMessage] = []

    def on_message(client, userdata, msg):
        received.append(msg)

    cliente_mqtt.on_message = on_message
    cliente_mqtt.subscribe("fabrica/#")
    cliente_mqtt.loop_start()

    try:
        contadores = publicar_mensagens(cliente_mqtt, mensagens, catalogo, 0.05)

        # Aguarda mensagens chegarem
        time.sleep(0.5)

        assert contadores["publicadas"] > 0, "Nenhuma mensagem publicada"
        assert contadores["publicadas"] >= 12, (
            f"Esperado >=12, publicado {contadores['publicadas']}"
        )
        assert len(received) > 0, "Nenhuma mensagem recebida via subscribe"

        # Verificar topicos recebidos
        topicos = {msg.topic for msg in received}
        assert any("telemetria" in t for t in topicos), f"Topicos: {topicos}"
        assert any("estado" in t for t in topicos), f"Topicos: {topicos}"
        assert any("parada" in t for t in topicos), f"Topicos: {topicos}"
        assert any("producao" in t for t in topicos), f"Topicos: {topicos}"
    finally:
        cliente_mqtt.loop_stop()


@pytest.mark.smoke
def test_maquina_fora_catalogo_pulada(cliente_mqtt, catalogo):
    """Mensagem com maquina_id fora do catalogo deve ser pulada."""
    mensagem_invalida = [
        {
            "schema": "telemetria.v1",
            "maquina_id": "MAQUINA-FANTASMA",
            "ts_sensor": "2026-03-10T13:45:02.140Z",
            "rpm": 100.0,
            "voltas_acumuladas": 1000,
            "temperatura_c": 40.0,
            "vibracao_mm_s": 1.0,
        }
    ]

    contadores = publicar_mensagens(cliente_mqtt, mensagem_invalida, catalogo, 0.01)

    assert contadores["publicadas"] == 0
    assert contadores["puladas"] == 1
