"""Consumidor MQTT — assinante assincrono que persiste mensagens no banco.

Pipeline: subscribe fabirca/# → validar (Pydantic) → hash → insert/dedup.
Dead-letter em data/dead-letter.ndjson para mensagens invalidas.

Uso:
    uv run python -m oee_textil.services.consumidor
"""

import asyncio
import contextlib
import hashlib
import json
import signal
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import aiomqtt
from sqlalchemy.dialects.postgresql import insert as pg_insert

from oee_textil.core.config import get_mqtt_broker_host, get_mqtt_broker_port
from oee_textil.core.database import SessionLocal
from oee_textil.models.estado import EstadoMaquina
from oee_textil.models.parada import Parada
from oee_textil.models.producao import Producao
from oee_textil.models.telemetria import Telemetria
from oee_textil.schemas.mensagens import MensagemMQTT

# --- Constantes ---

SCHEMA_PARA_MODELO: dict[str, type] = {
    "telemetria.v1": Telemetria,
    "estado.v1": EstadoMaquina,
    "parada.v1": Parada,
    "producao.v1": Producao,
}

# Campos a excluir do hash (nao fazem parte da identidade do evento)
CAMPOS_EXCLUIDOS_HASH = {"ts_ingestao", "id", "content_hash"}

# Caminho do arquivo de dead-letter (relativo ao repo root)
DEAD_LETTER_PATH = Path("data/dead-letter.ndjson")


# --- Helpers ---


def calcular_content_hash(dados: dict[str, Any]) -> str:
    """Calcula SHA-256 dos campos relevantes (exclui ts_ingestao, id).

    O hash e deterministico e ignora campos de infraestrutura como
    ts_ingestao (timestamp do servidor) e id (surrogate gerado pelo banco).
    """
    campos_relevantes = {
        k: v for k, v in dados.items() if k not in CAMPOS_EXCLUIDOS_HASH
    }
    canonico = json.dumps(campos_relevantes, sort_keys=True, default=str)
    return hashlib.sha256(canonico.encode()).hexdigest()


def resolver_tabela(schema: str) -> type:
    """Mapeia schema versionado (ex.: 'telemetria.v1') para modelo ORM."""
    modelo = SCHEMA_PARA_MODELO.get(schema)
    if modelo is None:
        raise ValueError(f"Schema desconhecido: {schema}")
    return modelo


def dead_letter(
    payload: dict[str, Any],
    erro: str,
    topico: str,
    caminho: Path | None = None,
) -> None:
    """Appenda mensagem invalida no arquivo dead-letter (NDJSON).

    Args:
        payload: Payload original da mensagem.
        erro: Descricao do erro de validacao.
        topico: Topico MQTT de origem.
        caminho: Caminho do arquivo dead-letter. Default: DEAD_LETTER_PATH.
    """
    destino = caminho or DEAD_LETTER_PATH
    destino.parent.mkdir(parents=True, exist_ok=True)

    registro = {
        "payload": payload,
        "erro": erro,
        "topico": topico,
        "ts_ingestao": datetime.now(UTC).isoformat(),
    }

    with open(destino, "a", encoding="utf-8") as f:
        f.write(json.dumps(registro, default=str) + "\n")


def inserir_telemetria(dados: dict[str, Any]) -> bool:
    """Insere telemetria com ON CONFLICT na PK natural (maquina_id, ts_sensor).

    Returns:
        True se inseriu, False se duplicata (ignorada).
    """
    with SessionLocal() as session:
        try:
            stmt = (
                pg_insert(Telemetria)
                .values(**dados)
                .on_conflict_do_nothing(
                    index_elements=["maquina_id", "ts_sensor"],
                )
            )
            result = session.execute(stmt)
            session.commit()
            return result.rowcount > 0  # type: ignore[attr-defined,no-any-return]
        except Exception:
            session.rollback()
            raise


def inserir_evento(
    modelo: type[EstadoMaquina | Parada | Producao],
    dados: dict[str, Any],
) -> bool:
    """Insere evento com ON CONFLICT no content_hash.

    Returns:
        True se inseriu, False se duplicata (ignorada).
    """
    # Copiar para nao mutar o dict original e evitar que content_hash
    # de uma chamada anterior contamine o calculo do hash.
    dados_insercao = dict(dados)
    dados_insercao["content_hash"] = calcular_content_hash(dados_insercao)

    with SessionLocal() as session:
        try:
            stmt = (
                pg_insert(modelo)
                .values(**dados_insercao)
                .on_conflict_do_nothing(
                    index_elements=["content_hash"],
                )
            )
            result = session.execute(stmt)
            session.commit()
            return result.rowcount > 0  # type: ignore[attr-defined,no-any-return]
        except Exception:
            session.rollback()
            raise


# --- Consumidor principal ---


async def processar_mensagem(
    topico: str,
    payload_str: str,
) -> None:
    """Pipeline completo de uma mensagem MQTT."""
    # 1. Parse JSON
    try:
        payload = json.loads(payload_str)
    except json.JSONDecodeError as e:
        dead_letter(
            {"raw": payload_str},
            f"JSON invalido: {e}",
            topico,
        )
        return

    # 2. Validar schema (Pydantic)
    try:
        msg = MensagemMQTT.validate_python(payload)
    except Exception as e:
        dead_letter(payload, f"Validacao schema: {e}", topico)
        return

    # 3. Extrair dados como dict
    dados = msg.model_dump()

    # 4. Resolver tabela e inserir
    schema = dados.get("schema", "")
    try:
        modelo = resolver_tabela(schema)
    except ValueError as e:
        dead_letter(payload, str(e), topico)
        return

    if modelo is Telemetria:
        inserir_telemetria(dados)
    else:
        inserir_evento(modelo, dados)


async def main() -> None:
    """Entry point do consumidor MQTT."""
    host = get_mqtt_broker_host()
    port = get_mqtt_broker_port()

    print(f"[CONSUMIDOR] Conectando ao broker {host}:{port}...")
    print("[CONSUMIDOR] Assinando fabrica/#")

    # Graceful shutdown
    running = True

    def _stop() -> None:
        nonlocal running
        print("\n[CONSUMIDOR] Sinal de parada recebido — finalizando...")
        running = False

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        with contextlib.suppress(NotImplementedError):
            loop.add_signal_handler(sig, _stop)

    try:
        async with aiomqtt.Client(
            hostname=host,
            port=port,
        ) as client:
            await client.subscribe("fabrica/#", qos=1)
            print("[CONSUMIDOR] Aguardando mensagens...")

            async for message in client.messages:
                if not running:
                    break
                topico = str(message.topic.value)
                payload_str = message.payload.decode()
                print(f"[{topico}] {payload_str[:80]}...")
                await processar_mensagem(topico, payload_str)
    except aiomqtt.MqttError as e:
        print(f"[CONSUMIDOR] Erro MQTT: {e}", file=sys.stderr)
        sys.exit(1)

    print("[CONSUMIDOR] Finalizado.")


if __name__ == "__main__":
    asyncio.run(main())
