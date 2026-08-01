"""CLI do simulador MQTT — le NDJSONs e publica no broker.

Uso:
    uv run python -m oee_textil.simulador [flags]
    uv run python -m oee_textil.simulador --interval 0.5 --speed 2 --loop
"""

import argparse
import signal
import sys
from pathlib import Path
from typing import Any

import paho.mqtt.client as mqtt

from oee_textil.simulador.catalogo import carregar_catalogo
from oee_textil.simulador.leitor import carregar_mensagens
from oee_textil.simulador.publisher import publicar_mensagens


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="oee-simulador",
        description="Simulador MQTT — publica dados de exemplo na topologia "
        "fabrica/{galpao}/{linha}/{maquina}/{tipo}",
    )
    parser.add_argument(
        "--broker-host",
        default="localhost",
        help="Host do broker MQTT (default: localhost)",
    )
    parser.add_argument(
        "--broker-port",
        type=int,
        default=1883,
        help="Porta do broker MQTT (default: 1883)",
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=1.0,
        help="Segundos entre mensagens (default: 1.0)",
    )
    parser.add_argument(
        "--speed",
        type=float,
        default=1.0,
        help="Multiplicador de velocidade (default: 1.0). "
        "Ex.: --speed 60 publica 1h de dados em ~1min",
    )
    parser.add_argument(
        "--loop",
        action="store_true",
        help="Repetir a sequencia de mensagens infinitamente",
    )
    parser.add_argument(
        "--data-dir",
        default="data/exemplos-mqtt",
        help="Diretorio com os arquivos NDJSON/CSV (default: data/exemplos-mqtt)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    """Entry point da CLI do simulador."""
    args = _parse_args(argv)

    # Resolver data_dir relativo a raiz do repo
    data_dir = _resolver_data_dir(args.data_dir)

    # Carregar dados
    print(f"[SIMULADOR] Carregando catalogo de {data_dir / 'maquinas.csv'}...")
    catalogo = carregar_catalogo(data_dir)
    print(f"[SIMULADOR] {len(catalogo)} maquinas carregadas.")

    print(f"[SIMULADOR] Carregando mensagens NDJSON de {data_dir}...")
    mensagens = carregar_mensagens(data_dir)
    if not mensagens:
        print("[SIMULADOR] Nenhuma mensagem carregada. Abortando.", file=sys.stderr)
        sys.exit(1)
    print(f"[SIMULADOR] {len(mensagens)} mensagens carregadas.")

    # Calcular intervalo efetivo
    if args.speed <= 0:
        print("[ERRO] --speed deve ser > 0", file=sys.stderr)
        sys.exit(1)
    intervalo_efetivo = args.interval / args.speed
    print(
        f"[SIMULADOR] Intervalo: {args.interval}s / speed {args.speed}x "
        f"= {intervalo_efetivo:.3f}s entre mensagens"
    )

    # Conectar MQTT
    cliente = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)  # type: ignore[attr-defined]
    cliente.connect(args.broker_host, args.broker_port)
    print(f"[SIMULADOR] Conectado ao broker {args.broker_host}:{args.broker_port}")

    # Tratar Ctrl+C
    running = True

    def _sigint_handler(signum: int, frame: Any) -> None:
        nonlocal running
        print("\n[SIMULADOR] Ctrl+C recebido — finalizando...")
        running = False

    signal.signal(signal.SIGINT, _sigint_handler)

    # Loop de publicacao
    ciclos = 0
    total_publicadas = 0
    total_puladas = 0

    try:
        while running:
            ciclos += 1
            if args.loop and ciclos > 1:
                print(f"[SIMULADOR] --- Ciclo {ciclos} ---")

            contadores = publicar_mensagens(
                cliente, mensagens, catalogo, intervalo_efetivo
            )
            total_publicadas += contadores["publicadas"]
            total_puladas += contadores["puladas"]

            if not args.loop:
                break
    finally:
        cliente.disconnect()
        print(
            f"[SIMULADOR] Finalizado. {total_publicadas} mensagens publicadas, "
            f"{total_puladas} puladas em {ciclos} ciclo(s)."
        )


def _resolver_data_dir(data_dir: str) -> Path:
    """Resolve o data_dir: se relativo, tenta relativo ao CWD ou ao repo root."""
    path = Path(data_dir)
    if path.is_absolute():
        return path

    # Tenta CWD primeiro
    cwd_path = Path.cwd() / path
    if cwd_path.exists():
        return cwd_path

    # Tenta relativo ao diretorio deste arquivo (src/oee_textil/simulador)
    repo_root = Path(__file__).resolve().parent.parent.parent.parent
    repo_path = repo_root / path
    if repo_path.exists():
        return repo_path

    # Fallback: retorna CWD (vai falhar com mensagem clara depois)
    return cwd_path
