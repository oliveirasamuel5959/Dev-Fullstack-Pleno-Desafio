# Plan — Fase 4: Modelo de dados

> Execução de [requirements.md](requirements.md). Grupos de tarefas numerados,
> executados **em ordem**; cada grupo termina em verificação + commit próprio.
> Critério de aceite final em [validation.md](validation.md).

## TG1 — Core (config + engine/session)

- **1.1** Criar `src/oee_textil/core/config.py`:
  - `DEFAULT_DATABASE_URL = "postgresql://oee:oee_dev@localhost:5432/oee_textil"`
  - `carregar_env(arquivo=None)`: procura `.env` no CWD ou repo root, lê
    `KEY=VALUE`, ignora `#` e linhas vazias, **não** sobrescreve vars
    existentes no `os.environ`.
  - `get_database_url() -> str`: `os.environ.get("DATABASE_URL", DEFAULT)`.
- **1.2** Criar `src/oee_textil/core/database.py`:
  - `Base = declarative_base()` (SQLAlchemy 2.0 `DeclarativeBase`)
  - `engine = create_engine(get_database_url(), pool_pre_ping=True)`
  - `SessionLocal = sessionmaker(bind=engine, expire_on_commit=False, autoflush=False)`
- **1.3** Atualizar docstring de `src/oee_textil/core/__init__.py`:
  - Remover menção a pydantic-settings; descrever config manual + engine.
- **1.4** Criar `.env` na raiz com `DATABASE_URL=...` (não versionado).
- **1.5** Criar `.env.example` na raiz (versionado) como template.
- **1.6** Criar `tests/test_config.py`:
  - `test_default_url` (sem env, sem .env → fallback)
  - `test_env_var_sobrescreve` (monkeypatch `DATABASE_URL`)
  - `test_carregar_env_le_arquivo` (tmp_path com `.env`)
  - `test_carregar_env_nao_sobrescreve_existente`
  - `test_carregar_env_arquivo_inexistente_noop`
- **Verificação:** `uv run pytest -k config -v` verde; `make lint`.
- **Commit:** `feat: core — DATABASE_URL via env com fallback dev e engine/sessão SQLAlchemy (Fase 4)`

## TG2 — Modelos ORM (7 tabelas)

- **2.1** Criar `src/oee_textil/models/maquina.py` — `Maquina`:
  PK `maquina_id`, `galpao`, `linha`, `tipo`, `tempo_ciclo_ideal_s`.
- **2.2** Criar `src/oee_textil/models/turno.py` — `Turno`:
  PK `turno_id`, `nome`, `inicio` (Time), `fim` (Time).
- **2.3** Criar `src/oee_textil/models/motivo_parada.py` — `MotivoParada`:
  PK `motivo_codigo`, `descricao`, `planejada`.
- **2.4** Criar `src/oee_textil/models/telemetria.py` — `Telemetria`:
  PK `(maquina_id, ts_sensor)`, FK→maquinas, `rpm`, `voltas_acumuladas`,
  `temperatura_c`, `vibracao_mm_s`, `ts_ingestao` com `server_default=now()`.
- **2.5** Criar `src/oee_textil/models/estado.py` — `EstadoMaquina`:
  `id` Identity PK, FK→maquinas, `ts_sensor`, `estado`, `estado_anterior`,
  `ts_ingestao`.
- **2.6** Criar `src/oee_textil/models/parada.py` — `Parada`:
  `id` Identity PK, FK→maquinas, FK→motivos_parada, `motivo_descricao`
  (denormalizado), `planejada` (denormalizado), `ts_sensor`, `ts_ingestao`.
- **2.7** Criar `src/oee_textil/models/producao.py` — `Producao`:
  `id` Identity PK, FK→maquinas, `ts_sensor`, `unidades_produzidas`,
  `unidades_refugo`, `ordem_producao`, `ts_ingestao`.
- **2.8** Atualizar `src/oee_textil/models/__init__.py`: importar todos os
  modelos para registrar no `Base.metadata` (Alembic precisa).
- **2.9** Criar `tests/test_models.py`:
  - `Base.metadata.tables` contém 7 tabelas
  - PK de `telemetria` = `(maquina_id, ts_sensor)`
  - `ts_sensor` e `ts_ingestao` com `timezone=True`
  - FKs: `parada → maquinas`, `parada → motivos_parada`, eventos → `maquinas`
  - `turnos.inicio/fim` do tipo `Time`
  - Índices esperados existem
  - `configure_mappers()` sem erro (valida relationships e forward refs)
- **Verificação:** `uv run pytest -k models -v` verde; `make lint`.
- **Commit:** `feat: modelos SQLAlchemy 2.0 — 7 tabelas incluindo hypertable de telemetria (Fase 4)`

## TG3 — Alembic + primeira migração

- **3.1** `uv run alembic init migrations`
- **3.2** Editar `alembic.ini`: esvaziar `sqlalchemy.url`, adicionar
  `prepend_sys_path = src`.
- **3.3** Reescrever `migrations/env.py`:
  - `from oee_textil.core.config import get_database_url`
  - `from oee_textil.core.database import Base`
  - `import oee_textil.models  # noqa: F401` (registra tabelas)
  - `target_metadata = Base.metadata`
  - `run_migrations_offline`/`run_migrations_online` com `get_database_url()`
- **3.4** Gerar migração com `--autogenerate` e revisar manualmente:
  - Adicionar `create_hypertable` via `op.get_context().autocommit_block()`
  - Verificar `server_default` em `ts_ingestao`
- **3.5** Testar: `make up` (garantir banco), `uv run alembic upgrade head`,
  `uv run alembic current`.
- **3.6** Testar round-trip: `downgrade base` → `upgrade head`.
- **3.7** Criar `tests/test_migrations.py` (smoke):
  - Tabela `alembic_version` existe
  - `telemetria` está em `timescaledb_information.hypertables`
- **Verificação:** `make up && make migrate && make migrate-current` mostra
  head; `uv run pytest -k migrations -v` verde.
- **Commit:** `feat: Alembic init + migração inicial com hypertable de telemetria (Fase 4)`

## TG4 — Seed + Makefile

- **4.1** Criar `src/oee_textil/seed.py`:
  - `_ler_csv(caminho) -> list[dict[str, str]]` — `csv.DictReader` com filtro
    de `#`
  - `TURNOS`: constante com 3 turnos fixos
  - `seed_maquinas(session, data_dir)`, `seed_motivos_parada(session, data_dir)`,
    `seed_turnos(session)` — cada uma com upsert idempotente
  - `main(argv)` com argparse (`--data-dir`), orquestração e resumo
  - `if __name__ == "__main__": main()`
- **4.2** Atualizar `Makefile`: adicionar targets `migrate`, `migrate-revision`,
  `migrate-down`, `migrate-history`, `migrate-current`, `seed`, `setup-db`.
- **4.3** Criar `tests/test_seed.py` (smoke):
  - Após seed, counts: maquinas=4, motivos_parada=7, turnos=3
  - Idempotência: rodar seed 2× → counts inalterados
- **Verificação:** `make setup-db && make seed` (2×); `make migrate-history`;
  `uv run pytest -k seed -v`.
- **Commit:** `feat: seed idempotente de maquinas/motivos/turnos via CSVs + Makefile DB targets (Fase 4)`

## TG5 — Gates finais e registros

- **5.1** Criar `docs/adr/003-modelagem-dados-raw-first-hypertable.md` a partir
  do template.
- **5.2** Atualizar `docs/AI_ASSISTED.md`: entrada da Fase 4.
- **5.3** Rodar barra completa: `make lint`, `make test` (todos os testes).
- **5.4** Executar o procedimento de [validation.md](validation.md).
- **5.5** Verificar round-trip completo: `make clean && make up && make setup-db
  && make lint && make test`.
- **Verificação:** todos os gates verdes; Fases 0–3 sem regressão.
- **Commit:** `docs: ADR-003 modelagem de dados + registro AI_ASSISTED (Fase 4)` → push.
