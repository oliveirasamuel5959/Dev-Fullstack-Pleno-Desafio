"""Seed idempotente das tabelas de catalogo a partir dos CSVs.

Le maquinas.csv e motivos-parada.csv de data/exemplos-mqtt/, popula as tabelas
maquinas e motivos_parada, e insere os 3 turnos fixos (Manha/Tarde/Noite).
Upsert via ON CONFLICT DO NOTHING — re-executavel sem duplicar dados.

Uso:
    uv run python -m oee_textil.seed
    uv run python -m oee_textil.seed --data-dir data/exemplos-mqtt
"""

import argparse
import csv
import sys
from datetime import time
from pathlib import Path
from typing import Any

from sqlalchemy.dialects.postgresql import insert as pg_insert

from oee_textil.core.database import SessionLocal
from oee_textil.models.maquina import Maquina
from oee_textil.models.motivo_parada import MotivoParada
from oee_textil.models.turno import Turno

# --- Constantes ---

TURNOS: list[dict[str, Any]] = [
    {"turno_id": "manha", "nome": "Manha", "inicio": time(6, 0), "fim": time(14, 0)},
    {"turno_id": "tarde", "nome": "Tarde", "inicio": time(14, 0), "fim": time(22, 0)},
    {"turno_id": "noite", "nome": "Noite", "inicio": time(22, 0), "fim": time(6, 0)},
]


# --- Helpers ---


def _ler_csv(caminho: Path) -> list[dict[str, str]]:
    """Le CSV com filtro de linhas de comentario (comecam com #)."""
    if not caminho.exists():
        print(f"[SEED] Arquivo nao encontrado: {caminho}", file=sys.stderr)
        return []

    with open(caminho, encoding="utf-8") as f:
        reader = csv.DictReader(
            (linha for linha in f if not linha.startswith("#")),
        )
        return list(reader)


def _resolver_data_dir(data_dir: str) -> Path:
    """Resolve data_dir: se relativo, tenta CWD ou repo root."""
    path = Path(data_dir)
    if path.is_absolute():
        return path

    cwd_path = Path.cwd() / path
    if cwd_path.exists():
        return cwd_path

    repo_root = Path(__file__).resolve().parents[3]
    repo_path = repo_root / path
    if repo_path.exists():
        return repo_path

    return cwd_path


# --- Funcoes de seed ---


def seed_maquinas(session: Any, data_dir: Path) -> int:
    """Popula maquinas a partir de maquinas.csv. Retorna count inserido."""
    rows = _ler_csv(data_dir / "maquinas.csv")
    if not rows:
        return 0

    stmt = pg_insert(Maquina).values(rows).on_conflict_do_nothing()
    result = session.execute(stmt)
    return result.rowcount  # type: ignore[no-any-return]


def seed_motivos_parada(session: Any, data_dir: Path) -> int:
    """Popula motivos_parada a partir de motivos-parada.csv."""
    rows_raw = _ler_csv(data_dir / "motivos-parada.csv")
    if not rows_raw:
        return 0

    # Converter planejada de string para bool e construir dicts tipados
    rows: list[dict[str, Any]] = [
        {
            "motivo_codigo": r["motivo_codigo"],
            "descricao": r["descricao"],
            "planejada": r["planejada"].lower() == "true",
        }
        for r in rows_raw
    ]

    stmt = pg_insert(MotivoParada).values(rows).on_conflict_do_nothing()
    result = session.execute(stmt)
    return result.rowcount  # type: ignore[no-any-return]


def seed_turnos(session: Any) -> int:
    """Popula turnos com os 3 turnos fixos de 8h."""
    stmt = pg_insert(Turno).values(TURNOS).on_conflict_do_nothing()
    result = session.execute(stmt)
    return result.rowcount  # type: ignore[no-any-return]


# --- CLI ---


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="oee-seed",
        description="Popula tabelas de catalogo (maquinas, motivos, turnos) "
        "a partir dos CSVs de exemplo.",
    )
    parser.add_argument(
        "--data-dir",
        default="data/exemplos-mqtt",
        help="Diretorio com maquinas.csv e motivos-parada.csv "
        "(default: data/exemplos-mqtt)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    """Entry point do seed."""
    args = _parse_args(argv)

    data_dir = _resolver_data_dir(args.data_dir)
    print(f"[SEED] Diretorio de dados: {data_dir}")

    # Usar o engine para criar tabelas se nao existirem (defensivo)
    # mas a migracao Alembic deve ter sido executada antes (make migrate)
    with SessionLocal() as session:
        try:
            n_maquinas = seed_maquinas(session, data_dir)
            n_motivos = seed_motivos_parada(session, data_dir)
            n_turnos = seed_turnos(session)
            session.commit()

            print(
                f"[SEED] {n_maquinas} maquinas, {n_motivos} motivos, {n_turnos} turnos"
            )
        except Exception:
            session.rollback()
            raise


if __name__ == "__main__":
    main()
