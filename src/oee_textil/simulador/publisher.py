"""Publicador MQTT — envia mensagens NDJSON para o broker na topologia
fabrica/{galpao}/{linha}/{maquina}/{tipo}.
"""

import sys
import time
from typing import Any

import paho.mqtt.client as mqtt

from oee_textil.schemas.mensagens import MensagemMQTT


def _construir_topico(
    schema: str, catalogo: dict[str, tuple[str, str]], maquina_id: str
) -> str:
    """Monta o topico MQTT a partir do schema e catalogo.

    Returns:
        Topico no formato fabrica/{galpao}/{linha}/{maquina}/{tipo}.
    """
    galpao, linha = catalogo[maquina_id]

    tipo_por_schema = {
        "telemetria.v1": "telemetria",
        "estado.v1": "estado",
        "parada.v1": "parada",
        "producao.v1": "producao",
    }
    tipo = tipo_por_schema[schema]

    return f"fabrica/{galpao}/{linha}/{maquina_id}/{tipo}"


def publicar_mensagens(
    cliente: mqtt.Client,
    mensagens: list[dict[str, Any]],
    catalogo: dict[str, tuple[str, str]],
    intervalo: float,
) -> dict[str, int]:
    """Itera sobre mensagens, valida, publica no topico correto.

    Args:
        cliente: Cliente paho-mqtt ja conectado.
        mensagens: Lista de dicts JSON carregados dos NDJSON.
        catalogo: Dicionario {maquina_id: (galpao, linha)}.
        intervalo: Segundos entre mensagens.

    Returns:
        Dicionario com contadores: {"publicadas": N, "puladas": N}.
    """
    contadores = {"publicadas": 0, "puladas": 0}

    for i, dados in enumerate(mensagens):
        try:
            msg = MensagemMQTT.validate_python(dados)
        except Exception as e:
            print(
                f"[AVISO] Mensagem {i + 1} falhou validacao: {e}",
                file=sys.stderr,
            )
            contadores["puladas"] += 1
            continue

        maquina_id: str = msg.maquina_id
        schema: str = msg.schema
        ts: object = msg.ts_sensor

        # Resolver topico
        if maquina_id not in catalogo:
            print(
                f"[AVISO] Maquina '{maquina_id}' nao encontrada no catalogo — pulando",
                file=sys.stderr,
            )
            contadores["puladas"] += 1
            continue

        topico = _construir_topico(schema, catalogo, maquina_id)

        # Publicar com QoS 1
        payload = dados  # reutiliza o dict original (ja validado)
        cliente.publish(topico, str(payload), qos=1)

        print(f"[{topico}] {schema} — {maquina_id} @ {ts}")

        contadores["publicadas"] += 1

        # Intervalo entre mensagens
        if i < len(mensagens) - 1:
            time.sleep(intervalo)

    return contadores
