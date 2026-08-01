# Plan — Fase 5: Consumidor de ingestão

> Execução de [requirements.md](requirements.md). Grupos de tarefas numerados,
> executados **em ordem**; cada grupo termina em verificação + commit próprio.
> Critério de aceite final em [validation.md](validation.md).

## TG1 — Dependência aiomqtt + config MQTT

- **1.1** `uv add aiomqtt`
- **1.2** Adicionar a `src/oee_textil/core/config.py`:
  - `DEFAULT_MQTT_BROKER_HOST = "localhost"`
  - `DEFAULT_MQTT_BROKER_PORT = 1883`
  - `get_mqtt_broker_host() -> str`
  - `get_mqtt_broker_port() -> int`
- **1.3** Atualizar `.env` e `.env.example` com `MQTT_BROKER_HOST` e
  `MQTT_BROKER_PORT`.
- **1.4** Atualizar `tests/test_config.py` com testes para as novas funções.
- **Verificação:** `uv run pytest -k config -v` verde (10+ testes).
- **Commit:** `feat: dependência aiomqtt + config MQTT broker (Fase 5)`

## TG2 — Migração: content_hash para dedup de eventos

- **2.1** `uv run alembic revision --autogenerate -m "adiciona content_hash unique em estado_maquina, parada, producao"`
- **2.2** Editar a migração manualmente:
  - `op.add_column("estado_maquina", sa.Column("content_hash", sa.String(64), nullable=True))`
  - Ídem para `parada` e `producao`
  - `op.create_unique_constraint("uq_estado_maquina_hash", "estado_maquina", ["content_hash"])`
  - Ídem para as outras duas
- **2.3** Atualizar `tests/test_models.py`: verificar que as 3 tabelas têm
  coluna `content_hash` e unique constraint.
- **2.4** Aplicar migração: `make migrate`
- **Verificação:** `uv run pytest -k migrations -v` verde; round-trip ok.
- **Commit:** `feat: migração — content_hash UNIQUE para dedup de eventos (Fase 5)`

## TG3 — Consumidor (subscribe, validate, hash, insert, dead-letter)

- **3.1** Criar `src/oee_textil/services/consumidor.py`:
  - `calcular_content_hash(msg: BaseModel) -> str`: SHA-256 dos campos
    relevantes (exclui ts_ingestao, id)
  - `resolver_tabela(schema: str) -> type[Base]`: mapeia schema→modelo ORM
  - `inserir(session, modelo, dados) -> bool`: INSERT com ON CONFLICT
  - `dead_letter(payload, erro, topico) -> None`: append em NDJSON
  - `async def main()`: subscribe `fabrica/#`, pipeline por mensagem,
    graceful shutdown com SIGINT/SIGTERM
  - Buffer de ordenação: `defaultdict[maquina_id, list]` com janela de 30s
- **3.2** Criar `src/oee_textil/services/__main__.py`:
  - `from oee_textil.services.consumidor import main; asyncio.run(main())`
- **3.3** Criar `tests/test_consumidor.py`:
  - `test_calcular_hash_deterministico`: mesmo input → mesmo hash
  - `test_calcular_hash_diferente_por_conteudo`: inputs diferentes → hashes diferentes
  - `test_calcular_hash_ignora_ts_ingestao`: mesmo payload, ts_ingestao diferente → mesmo hash
  - `test_resolver_tabela`: schema→modelo correto
  - `test_dead_letter_escreve_arquivo`: append gera NDJSON válido
  - `test_inserir_telemetria_dedup_natural`: ON CONFLICT na PK natural
  - `test_inserir_evento_dedup_hash`: ON CONFLICT no content_hash
  - `test_consumidor_ponta_a_ponta` (smoke): simulador publica, consumidor
    processa, verifica rows no banco, duplicata do fixture gera exatamente
    1 row
- **Verificação:** `uv run pytest -k consumidor -v` verde.
- **Commit:** `feat: consumidor MQTT assíncrono — validação, dedup, persistência, dead-letter (Fase 5)`

## TG4 — Dockerfile + compose service

- **4.1** Criar `Dockerfile` na raiz:
  - Multi-estágio: `FROM python:3.14-slim`
  - Copia `pyproject.toml` + `uv.lock`, `uv sync` (cache layer)
  - Copia `src/`, `data/`, `migrations/`, `alembic.ini`
  - `CMD ["python", "-m", "oee_textil.services.consumidor"]`
- **4.2** Adicionar serviço `consumidor` ao `docker-compose.yml`:
  - `build: .`, rede `oee-network`
  - `depends_on: mosquitto (healthy), timescaledb (healthy)`
  - Volumes: `./data:/app/data` (dead-letter)
  - Env vars: `DATABASE_URL`, `MQTT_BROKER_HOST=mosquitto`, `MQTT_BROKER_PORT=1883`
- **4.3** Adicionar target `build` ao Makefile.
- **Verificação:** `docker compose build consumidor`; `docker compose up -d`;
  `docker compose ps` mostra consumidor rodando.
- **Commit:** `feat: Dockerfile + serviço consumidor no compose (Fase 5)`

## TG5 — ADR-004 + gates finais

- **5.1** Criar `docs/adr/004-idempotencia-ordenacao-backpressure.md`
- **5.2** Atualizar `docs/AI_ASSISTED.md`: entrada da Fase 5
- **5.3** Barra completa: `make lint && make test`
- **5.4** Executar [validation.md](validation.md)
- **Verificação:** todos os gates verdes; fluxo ponta a ponta funcional
- **Commit:** `docs: ADR-004 idempotência + registro AI_ASSISTED (Fase 5)` → push
