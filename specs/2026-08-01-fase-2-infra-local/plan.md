# Plan — Fase 2: Infra local

> Execução de [requirements.md](requirements.md). Grupos de tarefas numerados,
> executados **em ordem**; cada grupo termina em verificação + commit próprio.
> Critério de aceite final em [validation.md](validation.md).

## TG1 — Estrutura e docker-compose.yml

- **1.1** Criar diretórios `docker/mosquitto/` e `docker/timescaledb/`.
- **1.2** Criar `docker-compose.yml` na raiz com:
  - Serviço `mosquitto`: imagem `eclipse-mosquitto:2`, porta `1883:1883`, bind
    mount `./docker/mosquitto/mosquitto.conf:/mosquitto/config/mosquitto.conf`,
    healthcheck com `mosquitto_sub -t '$SYS/#' -C 1 -T 5` (timeout 5s).
  - Serviço `timescaledb`: imagem `timescale/timescaledb:latest-pg16`, porta
    `5432:5432`, env vars `POSTGRES_USER=oee`, `POSTGRES_PASSWORD=oee_dev`,
    `POSTGRES_DB=oee_textil`, volume `pgdata:/var/lib/postgresql/data`, bind
    mount `./docker/timescaledb/init.sql:/docker-entrypoint-initdb.d/init.sql`,
    healthcheck com `pg_isready -U oee -d oee_textil`.
  - Rede `oee-network` (bridge).
  - Volume `pgdata`.
- **1.3** Criar `docker/mosquitto/mosquitto.conf`:
  ```
  listener 1883
  allow_anonymous true
  persistence false
  ```
- **1.4** Criar `docker/timescaledb/init.sql`:
  ```sql
  -- Init script para TimescaleDB — Fase 2.
  -- O banco oee_textil já é criado via POSTGRES_DB.
  -- A extensão TimescaleDB é habilitada aqui.
  CREATE EXTENSION IF NOT EXISTS timescaledb;
  ```
- **Verificação:** `docker compose up -d` sobe ambos; `docker compose ps` mostra
  status healthy em ambos.
- **Commit:** `feat: docker-compose com mosquitto + timescaledb`

## TG2 — Smoke test programático

- **2.1** `uv add paho-mqtt psycopg2-binary sqlalchemy` (dependências novas).
- **2.2** Criar `tests/test_smoke.py`:
  - `test_mosquitto_connect()`: conecta ao broker em `localhost:1883` via
    `paho.mqtt.client`, faz subscribe em tópico de teste, publica mensagem,
    verifica recebimento em até 5s. Usa `pytest.mark.smoke`.
  - `test_timescaledb_connect()`: conecta via SQLAlchemy com URL
    `postgresql://oee:oee_dev@localhost:5432/oee_textil`, executa `SELECT 1`,
    verifica resultado. Usa `pytest.mark.smoke`.
  - Ambos os testes devem ter timeout/wait adequado (containers podem estar
    subindo; até 10s de retry é razoável).
- **2.3** Registrar `smoke` no `[tool.pytest.ini_options].markers` do
  `pyproject.toml`.
- **Verificação:** `uv run pytest -k smoke -v` verde com containers rodando.
- **Commit:** `test: smoke test de conectividade mosquitto + timescaledb`

## TG3 — Makefile

- **3.1** Criar `Makefile` na raiz do repositório com targets:
  ```makefile
  .PHONY: up down ps logs test-smoke test lint clean

  up:
  	docker compose up -d

  down:
  	docker compose down

  ps:
  	docker compose ps

  logs:
  	docker compose logs -f

  test-smoke:
  	uv run pytest -k smoke -v

  test:
  	uv run pytest -v

  lint:
  	uv run ruff check && uv run ruff format --check && uv run mypy

  clean:
  	docker compose down -v
  ```
- **3.2** Garantir que `make` sem argumentos (ou `make help`) lista os targets
  disponíveis com descrição curta.
- **Verificação:** `make help` lista targets; `make up` sobe a infra; `make
  test-smoke` roda smoke tests.
- **Commit:** `feat: Makefile com comandos principais (up, test-smoke, lint)`

## TG4 — Gates finais e registros

- **4.1** Rodar a barra completa: `make lint` (ruff + mypy), `make test` (todos
  os testes incluindo smoke).
- **4.2** Atualizar `docs/AI_ASSISTED.md`: entrada da Fase 2.
- **4.3** Executar o procedimento de [validation.md](validation.md).
- **Verificação:** todos os gates verdes; smoke tests passam com infra rodando.
- **Commit:** `docs: registro AI_ASSISTED (Fase 2)` → push.
