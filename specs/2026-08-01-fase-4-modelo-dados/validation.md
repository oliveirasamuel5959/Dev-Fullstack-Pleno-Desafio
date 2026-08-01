# Validation — Fase 4: Modelo de dados

> Procedimento executável de validação da Fase 4. Rode as verificações abaixo
> **na ordem** após executar todos os grupos de tarefas de [plan.md](plan.md).
> Referência de requisitos: [requirements.md](requirements.md).
> Critério de saída do [roadmap](../../specs/roadmap.md): `uv run alembic
> upgrade head` aplica limpo; tabelas populadas.

---

## V1 — Core e .env (TG1)

- [ ] **1.1** `src/oee_textil/core/config.py` existe com `carregar_env()` e
  `get_database_url()`.
- [ ] **1.2** `src/oee_textil/core/database.py` existe com `Base`, `engine`,
  `SessionLocal`.
- [ ] **1.3** `.env` existe na raiz com `DATABASE_URL=...` (não versionado).
- [ ] **1.4** `.env.example` existe na raiz (versionado).
- [ ] **1.5** `test_default_url`: sem env → fallback dev.
- [ ] **1.6** `test_env_var_sobrescreve`: `DATABASE_URL` custom prevalece.
- [ ] **1.7** `test_carregar_env_le_arquivo`: `.env` em tmp_path é carregado.
- [ ] **1.8** Testes passam:
  ```bash
  uv run pytest -k config -v
  ```

---

## V2 — Modelos ORM (TG2)

- [ ] **2.1** 7 arquivos de modelo em `src/oee_textil/models/`:
  `maquina.py`, `turno.py`, `motivo_parada.py`, `telemetria.py`,
  `estado.py`, `parada.py`, `producao.py`.
- [ ] **2.2** `models/__init__.py` importa todos os modelos.
- [ ] **2.3** `Base.metadata.tables` contém 7 nomes:
  `maquinas`, `turnos`, `motivos_parada`, `telemetria`, `estado_maquina`,
  `parada`, `producao`.
- [ ] **2.4** PK de `telemetria` é composta: `(maquina_id, ts_sensor)`.
- [ ] **2.5** Colunas `ts_sensor` e `ts_ingestao` têm `timezone=True`.
- [ ] **2.6** FKs verificadas: `parada → maquinas`, `parada → motivos_parada`,
  eventos → `maquinas`.
- [ ] **2.7** `configure_mappers()` não levanta erro.
- [ ] **2.8** Testes passam:
  ```bash
  uv run pytest -k models -v
  ```

---

## V3 — Alembic e migração (TG3)

- [ ] **3.1** `alembic.ini` existe com `sqlalchemy.url =` (vazio) e
  `prepend_sys_path = src`.
- [ ] **3.2** `migrations/env.py` usa `get_database_url()` e
  `target_metadata = Base.metadata`.
- [ ] **3.3** Pelo menos 1 migração em `migrations/versions/`.
- [ ] **3.4** `uv run alembic upgrade head` aplica limpo (sem erro):
  ```bash
  make up && make migrate
  ```
- [ ] **3.5** `uv run alembic current` mostra o head.
- [ ] **3.6** Round-trip funciona:
  ```bash
  make migrate-down  # downgrade -1
  make migrate       # upgrade novamente
  ```
- [ ] **3.7** Tabelas existem no banco:
  ```bash
  psql -h localhost -U oee -d oee_textil -c "\dt"
  ```
- [ ] **3.8** `telemetria` é hypertable:
  ```bash
  psql -h localhost -U oee -d oee_textil -c "SELECT hypertable_name FROM timescaledb_information.hypertables;"
  ```
- [ ] **3.9** Testes de migração passam:
  ```bash
  uv run pytest -k migrations -v
  ```

---

## V4 — Seed e Makefile (TG4)

- [ ] **4.1** `src/oee_textil/seed.py` existe e é executável via
  `python -m oee_textil.seed`.
- [ ] **4.2** `make seed` popula as tabelas (4 máquinas, 7 motivos, 3 turnos).
- [ ] **4.3** Seed é idempotente:
  ```bash
  make seed && make seed  # segunda execução: mesmos counts, sem erro
  ```
- [ ] **4.4** Makefile tem todos os targets de DB:
  ```bash
  make help | grep -E "migrate|seed|setup-db"
  ```
- [ ] **4.5** `make setup-db` executa migrate + seed em sequência.
- [ ] **4.6** `make migrate-history` lista migrações.
- [ ] **4.7** `make migrate-current` mostra a migração atual.
- [ ] **4.8** Testes de seed passam:
  ```bash
  uv run pytest -k seed -v
  ```

---

## V5 — Gates de qualidade (TG5)

- [ ] **5.1** `make lint` verde (ruff check + ruff format --check + mypy).
- [ ] **5.2** `make test` verde (todos os testes).
- [ ] **5.3** `make test-smoke` verde (smoke tests com infra).
- [ ] **5.4** Fases 0–3 sem regressão:
  ```bash
  uv run pytest -k "not config and not models and not migrations and not seed" -v
  ```

---

## V6 — Registros (TG5)

- [ ] **6.1** `docs/adr/003-modelagem-dados-raw-first-hypertable.md` existe e
  segue o template.
- [ ] **6.2** `docs/AI_ASSISTED.md` tem entrada da Fase 4 preenchida.
- [ ] **6.3** `specs/roadmap.md` atualizado se necessário (ADR-003 referenciado).

---

## Fluxo completo de validação

```bash
# 1. Começar limpo
make clean

# 2. Subir infra e preparar banco
make up
make setup-db

# 3. Verificar estado do banco
make migrate-current
make migrate-history

# 4. Rodar smoke tests com infra
make test-smoke

# 5. Rodar todos os testes
make test

# 6. Barra de qualidade
make lint

# 7. Testar idempotência do seed
make seed && make seed

# 8. Testar round-trip de migração
make migrate-down && make migrate

# 9. Verificar tabelas no banco
psql -h localhost -U oee -d oee_textil -c "\dt"
psql -h localhost -U oee -d oee_textil -c "SELECT * FROM maquinas;"
psql -h localhost -U oee -d oee_textil -c "SELECT * FROM turnos;"
psql -h localhost -U oee -d oee_textil -c "SELECT * FROM motivos_parada;"

echo "FASE 4: TODOS OS GATES VERDES"
```

---

## Resumo

| Verificação | Descrição | Resultado |
|-------------|-----------|-----------|
| V1 | Core (config + engine/session + .env) | ✅ / ❌ |
| V2 | Modelos ORM (7 tabelas, relationships, PKs) | ✅ / ❌ |
| V3 | Alembic + migração (hypertable, round-trip) | ✅ / ❌ |
| V4 | Seed (idempotente, Makefile targets) | ✅ / ❌ |
| V5 | Gates de qualidade (ruff, mypy, pytest sem regressão) | ✅ / ❌ |
| V6 | Registros (ADR-003, AI_ASSISTED.md) | ✅ / ❌ |

> **Fase 4 fechada quando:** todas as verificações V1–V6 = ✅ **e**
> `uv run alembic upgrade head` aplica limpo com tabelas populadas.
> **Fases 0–3 devem continuar verdes.**
