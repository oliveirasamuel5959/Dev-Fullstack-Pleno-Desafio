# OEE Têxtil — Walking Skeleton

[![CI](https://github.com/oliveirasamuel5959/Dev-Fullstack-Pleno-Desafio/actions/workflows/ci.yml/badge.svg)](https://github.com/oliveirasamuel5959/Dev-Fullstack-Pleno-Desafio/actions/workflows/ci.yml)

> Resposta ao **Desafio Técnico — Desenvolvedor(a) Pleno Full Stack**:
> arquitetura _event-driven_ para ingestão de dados IoT (MQTT) e dashboard
> operacional de **OEE** para a indústria têxtil fictícia **Malharia Contínua
> S.A.** (3 galpões, ~200 máquinas, 3 turnos).
>
> **Branch:** `desafio/samuel-oliveira`

---

## Como rodar

```bash
# 1. Subir infraestrutura (Mosquitto + TimescaleDB)
docker compose up -d

# 2. Aplicar migrations e popular catálogo
uv run alembic upgrade head
uv run python -m oee_textil.seed

# 3. Iniciar o simulador (publica fixtures MQTT)
uv run python -m oee_textil.simulador --loop

# 4. Subir API + consumidor
docker compose up -d --build

# 5. Abrir o dashboard
open http://localhost:8000/dashboard
```

**Serviços:**

| Serviço | Porta | Descrição |
|---------|-------|-----------|
| Mosquitto (MQTT) | 1883 | Broker MQTT — recebe telemetria das máquinas |
| TimescaleDB | 5432 | PostgreSQL 16 + TimescaleDB — séries temporais + catálogo |
| API REST | 8000 | FastAPI — endpoints OEE + OpenAPI em `/docs` |
| Dashboard | 8000 | HTML/JS vanilla em `/dashboard` — atualização SSE ao vivo |
| Consumidor | — | Assina MQTT, valida schemas, dedup, persiste |

---

## O que foi entregue

| Eixo | Evidência |
|------|-----------|
| **Arquitetura & Modelagem** | [`docs/ARQUITETURA.md`](docs/ARQUITETURA.md) — C4 Contexto + Contêiner (Mermaid), bounded contexts, fluxo de dados |
| **Event-Driven & MQTT** | 4 schemas versionados (Pydantic + JSON Schema), topologia `fabrica/{galpao}/{linha}/{maquina}/...`, QoS 1, idempotência (content hash + ON CONFLICT), dead-letter NDJSON — [ADR-002](docs/adr/002-versionamento-schema-evolucao-aditiva.md), [ADR-004](docs/adr/004-idempotencia-ordenacao-backpressure.md) |
| **Monorepo vs Microsserviços** | Modular Monolith (1 pacote, 1 imagem Docker, múltiplos entry points) — [ADR-001](docs/adr/001-monorepo-um-pacote-n-entry-points.md), [`docs/TRADEOFFS.md`](docs/TRADEOFFS.md) |
| **Estratégia de Nuvem** | Design AWS (IoT Core, ECS Fargate, RDS, CloudWatch) + C4 Deploy + Terraform esboço — [ADR-009](docs/adr/009-estrategia-nuvem-aws.md), [`infra/terraform/`](infra/terraform/) |
| **CI/CD** | GitHub Actions: lint → typecheck → test → build-and-smoke — [ADR-008](docs/adr/008-ci-cd-github-actions.md) |
| **Harness & IA** | ruff + mypy + pytest + pre-commit; 138 testes (unitários + integração + contract + golden OEE) — [`docs/AI_ASSISTED.md`](docs/AI_ASSISTED.md) |
| **Dados & OEE** | OEE = D × P × Q (produto, nunca média), hypertables TimescaleDB, golden test (≈0,79) — [ADR-003](docs/adr/003-modelagem-dados-raw-first-hypertable.md), [ADR-005](docs/adr/005-janelas-agregacao-late-events.md) |
| **Qualidade da Entrega** | 14 commits atômicos, 9 ADRs, DECISOES.md, TRADEOFFS.md, README reproducible |

### Documentação

| Documento | Conteúdo |
|-----------|----------|
| [`docs/ARQUITETURA.md`](docs/ARQUITETURA.md) | Visão geral, C4 Contexto + Contêiner, fluxo de dados, bounded contexts, glossário OEE |
| [`docs/TRADEOFFS.md`](docs/TRADEOFFS.md) | 6 trade-offs: monorepo vs micro, Mosquitto vs IoT Core, SSE vs WebSocket, PG vs Timestream, Python vs Go, Compose vs K8s |
| [`docs/DECISOES.md`](docs/DECISOES.md) | Justificativa de cada stack/ferramenta/biblioteca |
| [`docs/adr/`](docs/adr/) | 9 ADRs (001–009) cobrindo monorepo, schemas, dados, idempotência, OEE, API, SSE, CI/CD, nuvem |
| [`docs/AI_ASSISTED.md`](docs/AI_ASSISTED.md) | Registro de uso de IA (Fases 0–10), decisões, correções |
| [`specs/`](specs/) | Roadmap, mission, tech-stack + specs por fase |
| [`infra/terraform/`](infra/terraform/) | Esboço de infra AWS (IoT Core, ECS, RDS, SQS, ALB) |

---

## O que ficou de fora (e por quê)

| Item | Motivo |
|------|--------|
| **Ordenação de eventos com buffer** | Documentado como TODO no [ADR-004](docs/adr/004-idempotencia-ordenacao-backpressure.md). O foco da Fase 5 foi dedup e persistência; o buffer de 30s por máquina é uma melhoria planejada. |
| **Autenticação / Multi-tenant** | Não-objetivo da [missão](specs/mission.md) §6. O walking skeleton é single-tenant por design. |
| **Integração com broker real** | O [simulador](src/oee_textil/simulador.py) cobre o escopo do desafio. A migração para IoT Core está documentada no [ADR-009](docs/adr/009-estrategia-nuvem-aws.md). |
| **UI polida / gráficos** | O [dashboard](src/oee_textil/static/index.html) prova a arquitetura (SSE + REST), não o design. Gráficos complexos exigiram bibliotecas (Chart.js/D3) fora do escopo. |
| **Cobertura de código** | Não configurada. pytest cobre unitários, integração, contratos e golden test; coverage tool adicionaria complexidade sem valor no momento. |
| **Alertas / Notificações** | Fora do escopo da missão §6. O sistema calcula OEE; alertas (ex.: OEE < 60%) são camada de aplicação acima. |

---

## Estrutura do repositório

```
.
├── .github/workflows/ci.yml     # Pipeline CI/CD (GitHub Actions)
├── data/exemplos-mqtt/          # Fixtures MQTT (NDJSON + CSV)
├── docker/                      # Configs de container (mosquitto.conf, init.sql)
├── docs/
│   ├── adr/                     # 9 Architecture Decision Records (001–009)
│   ├── contracts/               # JSON Schema exportado (4 schemas MQTT)
│   ├── ARQUITETURA.md           # Visão arquitetural + C4
│   ├── DECISOES.md              # Justificativas de stack
│   ├── TRADEOFFS.md             # Trade-offs documentados
│   ├── AI_ASSISTED.md           # Registro de desenvolvimento assistido por IA
│   └── ENTREGAVEIS.md           # Checklist de entregáveis (rúbrica)
├── infra/terraform/             # Esboço de infra AWS (não applyável)
├── migrations/                  # Alembic migrations
├── specs/                       # Roadmap, missão, tech-stack + specs por fase
├── src/oee_textil/
│   ├── core/                    # Config, database (engine, session)
│   ├── models/                  # SQLAlchemy models (7 entidades)
│   ├── routes/                  # FastAPI routes (API REST + SSE)
│   ├── schemas/                 # Pydantic models (4 schemas MQTT)
│   ├── services/                # Consumidor MQTT, motor OEE
│   ├── static/                  # Dashboard HTML + CSS + JS vanilla
│   └── simulador.py             # CLI publicador MQTT
├── tests/                       # 138 testes (unit, integração, contract, smoke)
├── docker-compose.yml           # 4 serviços (mosquitto, timescaledb, consumidor, api)
├── Dockerfile                   # Imagem única, multi-entrypoint
├── Makefile                     # Entry point unificado (up, test, lint, etc.)
└── pyproject.toml               # Dependências + config ruff/mypy/pytest
```

---

## Comandos úteis

```bash
make help          # Lista todos os targets
make up            # Sobe Mosquitto + TimescaleDB
make build         # Build da imagem Docker
make test          # Roda pytest (todos os testes)
make test-smoke    # Roda só smoke tests (precisa de infra up)
make lint          # ruff check + format + mypy
make seed          # Popula catálogo (máquinas, motivos, turnos)
make clean         # docker compose down + remove volume
```
