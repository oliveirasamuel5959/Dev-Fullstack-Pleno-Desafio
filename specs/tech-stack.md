# Tech Stack

> Stack fixada para o _walking skeleton_. Cada escolha tem um **porquê** de uma
> linha — a defesa completa vive em `docs/DECISOES.md` e nos ADRs (ver
> [roadmap](roadmap.md)). Mudança de stack exige atualizar este arquivo **e**
> registrar o motivo.

## Runtime & gerenciador

| Escolha | Por quê |
|---------|---------|
| **Python 3.14** | Já fixado no scaffold (`.python-version`); tipagem forte com `mypy` para harness rigoroso. |
| **uv** | Gerenciador já em uso (`pyproject.toml` + `uv.lock`); resolução rápida e reproduzível. Comandos: `uv sync`, `uv add`, `uv run`. |

## API & tempo real

| Escolha | Por quê |
|---------|---------|
| **FastAPI + uvicorn** | Async nativo, OpenAPI gerada de graça (entregável da spec §5), SSE/WebSocket sem framework extra. |
| **SSE (Server-Sent Events)** | Fluxo unidirecional servidor→cliente com reconexão automática; o dashboard é somente-leitura — WebSocket seria complexidade sem ganho (ADR dedicado na Fase 8). |
| **Frontend: 1 página HTML + JS vanilla** | Servida pelo próprio FastAPI; o escopo é provar a arquitetura, não a UI (ver missão §6). |

## Mensageria

| Escolha | Por quê |
|---------|---------|
| **Eclipse Mosquitto** (container) | Broker MQTT de referência: QoS 0/1/2 completos, leve, trivial de containerizar — o eixo Event-Driven é avaliado _de verdade_, não simulado em processo. |
| **aiomqtt** | Cliente asyncio sobre o paho; encaixa no event loop do FastAPI sem threads extras. |

## Dados

| Escolha | Por quê |
|---------|---------|
| **PostgreSQL 16 + TimescaleDB** (imagem `timescale/timescaledb`) | Telemetria é série temporal de alta cardinalidade (~200 máquinas × 1–5 s): _hypertables_ dão o eixo "time-series" de graça; o mesmo banco resolve o núcleo relacional (máquinas, motivos, turnos, agregações de OEE). |
| **SQLAlchemy 2 + Alembic** | ORM maduro com migrações versionadas — reprodutibilidade é eixo avaliado. |

## Contratos

| Escolha | Por quê |
|---------|---------|
| **Pydantic v2** | Valida os 4 schemas (`telemetria.v1`, `estado.v1`, `parada.v1`, `producao.v1`) na borda do sistema e exporta **JSON Schema** para `docs/contracts/` — base dos _contract tests_ versionados. |

## Harness (quality gates)

| Escolha | Por quê |
|---------|---------|
| **pytest** | Testes unitários, de integração e o _self-check_ dourado do OEE (números de `docs/CONTEXTO_NEGOCIO.md` §2: D=0,875; Q=0,95; OEE≈0,79). |
| **ruff** (lint + format) | Um único linter rápido, configurado no `pyproject.toml`. |
| **mypy** | _Type checking_ estático como gate — código gerado (humano ou IA) só entra passando. |
| **Contract test de fixtures** | Cada linha de `data/exemplos-mqtt/*.ndjson` validada contra os schemas — incluindo o tratamento dos defeitos intencionais. |

## Infra & CI

| Escolha | Por quê |
|---------|---------|
| **docker compose** (mosquitto, timescaledb, app) | O esqueleto inteiro sobe com `docker compose up` — exigência do entregável. |
| **GitHub Actions** | CI nativo do repositório: ruff → mypy → pytest → smoke do compose como quality gates. |

## Nuvem

> **Decisão adiada por design** para a fase de nuvem do [roadmap](roadmap.md)
> (Fase 10), onde vira ADR próprio. Candidatos: AWS (IoT Core como MQTT
> gerenciado + Fargate + Timestream/RDS) — a escolha comparará gerenciado vs.
> self-hosted em custo, escala (~200 → 1.000+ máquinas) e observabilidade.
