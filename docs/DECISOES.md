# Decisões Técnicas

> Justificativa detalhada de cada escolha de stack, ferramenta e padrão.
> Conforme [`mission.md`](../specs/mission.md) §5: "Justificar cada decisão de
> stack/ferramenta/biblioteca". Decisões estruturais viram ADR (ver `adr/`).

## Stack principal

| Decisão | Justificativa | ADR |
|---------|---------------|-----|
| Python 3.14 | Fixado no scaffold inicial (`.python-version`); tipagem forte com `mypy` para harness rigoroso. | — |
| uv (gerenciador) | Já em uso no scaffold (`pyproject.toml` + `uv.lock`); resolução rápida e reprodutível; `uv run` unifica comandos. | — |
| Monorepo único | Um pacote Python (`src/oee_textil/`), uma imagem Docker, múltiplos entry points (`consumidor`, `simulador`, `api`). Walking skeleton não justifica orquestração multi-serviço. | [ADR-001](adr/001-monorepo-um-pacote-n-entry-points.md) |
| FastAPI + uvicorn | Async nativo, OpenAPI gerada de graça, SSE/WebSocket sem framework extra. | [ADR-006](adr/006-design-api-rest-fastapi.md) |
| SSE (Server-Sent Events) | Fluxo unidirecional servidor→cliente com reconexão automática; dashboard é somente-leitura. | [ADR-007](adr/007-sse-vs-websocket-polling.md) |
| Eclipse Mosquitto | Broker MQTT de referência: QoS 0/1/2 completos, leve, trivial de containerizar. | — |
| aiomqtt | Cliente MQTT asyncio sobre paho; encaixa no event loop do FastAPI sem threads extras. | — |
| PostgreSQL 16 + TimescaleDB | Telemetria é série temporal de alta cardinalidade (~200 máquinas × 1–5s); hypertables resolvem o eixo time-series. | [ADR-003](adr/003-modelagem-dados-raw-first-hypertable.md) |
| SQLAlchemy 2 + Alembic | ORM maduro com migrações versionadas; reprodutibilidade é eixo avaliado. | [ADR-003](adr/003-modelagem-dados-raw-first-hypertable.md) |
| Pydantic v2 | Validação de schemas MQTT na borda do sistema; exporta JSON Schema para contract tests. | [ADR-002](adr/002-versionamento-schema-evolucao-aditiva.md) |

## Mensageria & Event-Driven

| Decisão | Justificativa | ADR |
|---------|---------------|-----|
| Schemas versionados (`telemetria.v1`, etc.) | Evolução aditiva sem quebrar consumidores; campo `schema` como discriminator. | [ADR-002](adr/002-versionamento-schema-evolucao-aditiva.md) |
| QoS 1 (at least once) | Garante entrega exercitando idempotência no consumidor; alinhado com o eixo Event-Driven da avaliação. | — |
| Content hash para dedup | SHA-256 dos campos relevantes com constraint UNIQUE; eventos sem PK natural. | [ADR-004](adr/004-idempotencia-ordenacao-backpressure.md) |
| Dead-letter NDJSON | Mensagens inválidas são apensadas em arquivo rotativo em disco; volume no container. | [ADR-004](adr/004-idempotencia-ordenacao-backpressure.md) |

## OEE

| Decisão | Justificativa | ADR |
|---------|---------------|-----|
| OEE = D × P × Q (produto, não média) | Definido pela especificação técnica §4; clamping [0,1] com sinalização de dados inconsistentes. | — |
| Funções puras de cálculo | Testabilidade e reprodutibilidade; golden test com o exemplo do enunciado (≈0,79). | [ADR-005](adr/005-janelas-agregacao-late-events.md) |
| Janela aberta para fixtures (2020–hoje) | Os dados de exemplo têm timestamps de 2020; janela fixa de 30 dias excluiria o golden case. | [ADR-005](adr/005-janelas-agregacao-late-events.md) |

## Harness (quality gates)

| Decisão | Justificativa | ADR |
|---------|---------------|-----|
| pytest | Testes unitários, de integração e golden self-check do OEE. | — |
| ruff (lint + format) | Linter rápido e único; configurado no `pyproject.toml`. | — |
| mypy (strict) | Type checking estático como gate — código gerado (humano ou IA) só entra passando. | — |
| pre-commit hooks | Ruff + mypy executam antes de cada commit; barreira local contra regressões. | — |

## CI/CD

| Decisão | Justificativa | ADR |
|---------|---------------|-----|
| GitHub Actions | Nativo do repositório GitHub, zero infra extra; runner `ubuntu-latest` gratuito suficiente para o walking skeleton. | [ADR-008](adr/008-ci-cd-github-actions.md) |
| Pipeline sequencial (lint → typecheck → test → smoke) | Fail fast: não faz sentido rodar testes se o código não passa no linter. | [ADR-008](adr/008-ci-cd-github-actions.md) |
| Service containers do GHA (Mosquitto + TimescaleDB) | Testes de integração precisam de broker e banco reais; mock não exercita os eixos Event-Driven e Dados da avaliação. | [ADR-008](adr/008-ci-cd-github-actions.md) |
| Sem cache/matrix nesta fase | YAGNI: ~15 dependências, `uv sync` <30s; só Python 3.14 existe. | [ADR-008](adr/008-ci-cd-github-actions.md) |

## Nuvem

> **Decisão adiada** por design para a Fase 10 do roadmap, onde virará ADR
> próprio (ADR-006). Candidatos: AWS (IoT Core + Fargate + Timestream/RDS)
> comparando gerenciado vs. self-hosted em custo, escala e observabilidade.
