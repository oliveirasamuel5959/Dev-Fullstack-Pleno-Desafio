# Validation — Fase 2: Infra local

> Procedimento executável de validação da Fase 2. Rode as verificações abaixo
> **na ordem** após executar todos os grupos de tarefas de [plan.md](plan.md).
> Referência de requisitos: [requirements.md](requirements.md).
> Critério de saída do [roadmap](../../specs/roadmap.md): `docker compose up -d`
> sobe ambos; `docker compose ps` saudável.

---

## V1 — Estrutura e docker-compose (TG1)

- [ ] **1.1** Diretórios `docker/mosquitto/` e `docker/timescaledb/` existem.
- [ ] **1.2** `docker-compose.yml` existe na raiz com serviços `mosquitto` e
  `timescaledb`.
  ```bash
  docker compose config --quiet && echo "OK"
  ```
- [ ] **1.3** `docker/mosquitto/mosquitto.conf` existe com `listener 1883`,
  `allow_anonymous true`, `persistence false`.
- [ ] **1.4** `docker/timescaledb/init.sql` existe com
  `CREATE EXTENSION IF NOT EXISTS timescaledb`.
- [ ] **1.5** `docker compose up -d` sobe ambos os containers sem erro.
  ```bash
  docker compose up -d && echo "OK"
  ```
- [ ] **1.6** `docker compose ps` mostra ambos os serviços com status "healthy"
  (pode levar alguns segundos na primeira subida).
  ```bash
  docker compose ps
  ```
- [ ] **1.7** Porta `1883` responde (Mosquitto aceita conexão TCP).
  ```bash
  nc -z localhost 1883 && echo "Mosquitto OK"
  ```
- [ ] **1.8** Porta `5432` responde (TimescaleDB aceita conexão TCP).
  ```bash
  nc -z localhost 5432 && echo "TimescaleDB OK"
  ```

---

## V2 — Smoke test programático (TG2)

- [ ] **2.1** `paho-mqtt`, `psycopg2-binary` e `sqlalchemy` aparecem em
  `[project].dependencies` ou `[dependency-groups]` do `pyproject.toml`.
- [ ] **2.2** `tests/test_smoke.py` existe com funções `test_mosquitto_connect`
  e `test_timescaledb_connect`, ambas marcadas `@pytest.mark.smoke`.
- [ ] **2.3** Marker `smoke` registrado em `[tool.pytest.ini_options].markers`.
- [ ] **2.4** Smoke tests passam:
  ```bash
  uv run pytest -k smoke -v
  ```

---

## V3 — Makefile (TG3)

- [ ] **3.1** `Makefile` existe na raiz do repositório.
- [ ] **3.2** `make help` (ou `make` sem argumentos) lista os targets disponíveis.
- [ ] **3.3** `make up` sobe os containers.
  ```bash
  make down && make up && docker compose ps
  ```
- [ ] **3.4** `make test-smoke` executa `uv run pytest -k smoke -v` e passa.
- [ ] **3.5** `make ps` mostra status dos containers.
- [ ] **3.6** `make logs` mostra logs de ambos os serviços (verificar
  visualmente que Mosquitto loga "mosquitto version" e TimescaleDB loga
  "database system is ready").
- [ ] **3.7** `make down` para e remove os containers.
- [ ] **3.8** `make clean` remove containers + volume (dados perdidos).

---

## V4 — Gates de qualidade (TG4)

- [ ] **4.1** `make lint` (ruff check + ruff format --check + mypy) verde.
  ```bash
  make lint && echo "Lint OK"
  ```
- [ ] **4.2** `make test` (todos os testes) verde.
  ```bash
  make test && echo "Tests OK"
  ```
- [ ] **4.3** Testes da Fase 0 e Fase 1 continuam passando (sem regressão):
  ```bash
  uv run pytest -k "not smoke" -v
  ```
- [ ] **4.4** `docker compose down` limpa os containers ao final.

---

## V5 — Registros (TG4)

- [ ] **5.1** `docs/AI_ASSISTED.md` tem entrada da Fase 2 preenchida.
- [ ] **5.2** `README.md` ou documentação relevante menciona `make up` como
  ponto de partida.

---

## Fluxo completo de validação

```bash
# 1. Limpar estado anterior
make clean

# 2. Subir infra
make up

# 3. Aguardar healthchecks (pode levar ~10-15s na primeira vez)
sleep 10
make ps

# 4. Rodar smoke tests
make test-smoke

# 5. Rodar barra completa
make lint && make test

# 6. Verificar que Fases 0 e 1 continuam verdes
uv run pytest -k "not smoke" -v

# 7. Limpar
make down

echo "FASE 2: TODOS OS GATES VERDES"
```

---

## Resumo

| Verificação | Descrição | Resultado |
|-------------|-----------|-----------|
| V1 | Estrutura, docker-compose, containers healthy | ✅ / ❌ |
| V2 | Smoke test programático (Mosquitto + TimescaleDB) | ✅ / ❌ |
| V3 | Makefile (up, down, ps, logs, test-smoke, test, lint, clean) | ✅ / ❌ |
| V4 | Gates de qualidade (ruff, mypy, pytest sem regressão) | ✅ / ❌ |
| V5 | Registros (AI_ASSISTED.md, README) | ✅ / ❌ |

> **Fase 2 fechada quando:** todas as verificações V1–V5 = ✅.
> **Fases 0 e 1 devem continuar verdes** (smoke test da Fase 0 e contract tests
> da Fase 1 não podem quebrar).
