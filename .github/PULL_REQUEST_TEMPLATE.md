# Pull Request - Entrega do Desafio

> Preencha para nos ajudar na avaliação. Seja objetivo.

## Identificação
- **Nome:** Samuel Patrício de Oliveira
- **Link do fork (público):** https://github.com/oliveirasamuel5959/Dev-Fullstack-Pleno-Desafio/tree/desafio/samuel-oliveira
- **Tempo aproximado dedicado:** 48 horas para estudos e consolidação das ideias e 48 para implementação

## Resumo da arquitetura (2–4 linhas)

**Event-Driven + Modular Monolith.** Um pacote Python (`oee_textil`), uma imagem
Docker, múltiplos entry points (consumidor, API, simulador, seed). A comunicação
externa é assíncrona via **MQTT** (telemetria/eventos das ~200 máquinas têxteis)
e **SSE** (stream do dashboard). O banco **PostgreSQL + TimescaleDB** resolve o
núcleo relacional (catálogo, motivos, turnos) e as séries temporais (hypertables
de telemetria). Diagramas C4 (Contexto, Contêiner, Deploy AWS) em Mermaid no
[`docs/ARQUITETURA.md`](docs/ARQUITETURA.md).

## Decisões principais (e por quê)

- **Stack / linguagem:** Python 3.14 + FastAPI + SQLAlchemy 2 + Alembic. Stack
  única para API, consumidor e simulador — reduz carga cognitiva e custo de
  manutenção. Para ~200 máquinas a 5s de intervalo (~40 msg/s), Python com asyncio
  lida com folga. ([DECISOES.md](docs/DECISOES.md),
  [TRADEOFFS.md](docs/TRADEOFFS.md))

- **Mensageria / MQTT:** Eclipse Mosquitto (dev/local) → AWS IoT Core (prod).
  Topologia `fabrica/{galpao}/{linha}/{maquina}/{tipo}`. QoS 1 (at least once)
  para exercitar idempotência. Schemas versionados Pydantic v2
  (`telemetria.v1`, `estado.v1`, `parada.v1`, `producao.v1`). Content hash
  SHA-256 + ON CONFLICT para dedup; dead-letter NDJSON para inválidas.
  ([ADR-002](docs/adr/002-versionamento-schema-evolucao-aditiva.md),
  [ADR-004](docs/adr/004-idempotencia-ordenacao-backpressure.md))

- **Banco(s) de dados:** PostgreSQL 16 + TimescaleDB (hypertables com partição
  por `ts_sensor`). Mesmo banco para relacional + time-series — evita dois
  sistemas. Migrações versionadas com Alembic; seed idempotente dos CSVs de
  catálogo. ([ADR-003](docs/adr/003-modelagem-dados-raw-first-hypertable.md))

- **Monorepo vs. microsserviços:** Modular Monolith — 1 pacote, 1 imagem Docker,
  múltiplos entry points. O escopo do walking skeleton (~200 máquinas, 1 fábrica)
  não justifica orquestração multi-serviço. A modularização interna (`schemas/`,
  `models/`, `services/`, `routes/`) preserva a opção de extrair serviços no
  futuro. ([ADR-001](docs/adr/001-monorepo-um-pacote-n-entry-points.md))

- **Nuvem:** AWS — IoT Core (MQTT gerenciado), ECS Fargate (containers),
  RDS PostgreSQL + TimescaleDB, CloudWatch, S3, ALB + Route 53. Terraform
  esboço em [`infra/terraform/`](infra/terraform/). Custo estimado: ~$540/mês
  para ~200 máquinas. ([ADR-009](docs/adr/009-estrategia-nuvem-aws.md))

- **CI/CD:** GitHub Actions — pipeline sequencial (lint → typecheck → test →
  build-and-smoke). Service containers reais (Mosquitto + TimescaleDB) no job
  de teste. Migrations + seed antes do pytest. Push na branch `desafio/samuel-oliveira`
  + PR contra `main`. ([ADR-008](docs/adr/008-ci-cd-github-actions.md),
  [`.github/workflows/ci.yml`](.github/workflows/ci.yml))

## O que está implementado vs. descrito

- [x] Walking skeleton executável — `docker compose up` sobe 4 serviços
- [x] Contratos de mensagem / schema — 4 schemas Pydantic v2 + JSON Schema exportado
- [x] Cálculo de OEE — D × P × Q (produto, nunca média) + golden test (≈0,79)
- [x] Dashboard — HTML/JS vanilla com 4 cards + SSE ao vivo
- [x] Pipeline de CI/CD — GitHub Actions real (4 jobs, verde em push)
- [x] Harness — ruff + mypy strict + pytest (138 testes) + pre-commit hooks
- [x] AI_ASSISTED.md preenchido — Fases 0–10, decisões, correções, uso de IA

## Como rodar

### Pré-requisitos

- **Docker** (compose v2) — para subir Mosquitto, TimescaleDB, Consumidor e API
- **Python 3.14** + **uv** — para desenvolvimento local, testes e CLI do simulador
- **Gerenciador de banco de dados** (recomendado: DBeaver, pgAdmin ou `psql`) —
  para inspecionar hypertables, testar queries e validar agregações de OEE
- **Git** — para clonar o repositório

### Setup rápido (3 passos)

```bash
# 1. Clonar o repositório
git clone https://github.com/oliveirasamuel5959/Dev-Fullstack-Pleno-Desafio.git
cd Dev-Fullstack-Pleno-Desafio
git checkout desafio/samuel-oliveira

# 2. Subir infraestrutura (Mosquitto + TimescaleDB + Consumidor + API)
docker compose up -d

# 3. Aplicar migrations e popular catálogo
uv run alembic upgrade head
uv run python -m oee_textil.seed
```

### Simular tráfego MQTT (opcional — para ver o dashboard ao vivo)

```bash
# Publica as fixtures NDJSON/CSV em loop contínuo
uv run python -m oee_textil.simulador --loop
```

### Acessar

| URL | Conteúdo |
|-----|----------|
| `http://localhost:8000/dashboard` | Dashboard OEE ao vivo (SSE) |
| `http://localhost:8000/docs` | OpenAPI (Swagger UI) |
| `http://localhost:8000/api/v1/oee/atual` | OEE atual por máquina |
| `http://localhost:8000/api/v1/paradas/pareto` | Pareto de paradas |
| `http://localhost:8000/health` | Healthcheck da API |

### Comandos com Make (recomendado para reprodutibilidade)

```bash
make help          # Lista todos os targets disponíveis
make up            # Sobe Mosquitto + TimescaleDB
make build         # Build da imagem Docker
make seed          # Popula catálogo (máquinas, motivos, turnos)
make migrate       # Aplica migrations pendentes
make test          # Roda todos os testes (138)
make test-smoke    # Roda só smoke tests (requer infra up)
make lint          # ruff check + ruff format + mypy
make ps            # Verifica status dos containers
make down          # Para todos os containers
make clean         # Para tudo + remove volume pgdata
```

### Inspecionar o banco de dados (DBeaver ou similar)

```
Host:     localhost
Porta:    5432
Usuário:  oee
Senha:    oee_dev
Banco:    oee_textil
```

**Queries úteis para validação:**

```sql
-- Verificar hypertables
SELECT * FROM timescaledb_information.hypertables;

-- OEE agregado por máquina (últimas 24h)
SELECT maquina_id, AVG(oee) as oee_medio
FROM oee_agregado
WHERE janela_fim > NOW() - INTERVAL '24 hours'
GROUP BY maquina_id
ORDER BY oee_medio DESC;

-- Últimas 10 telemetrias
SELECT * FROM telemetria ORDER BY ts_sensor DESC LIMIT 10;

-- Top 5 motivos de parada (Pareto)
SELECT motivo_descricao, COUNT(*) as ocorrencias
FROM parada
GROUP BY motivo_descricao
ORDER BY ocorrencias DESC
LIMIT 5;
```

## O que eu deixei de fora conscientemente (e por quê)

| Item | Motivo |
|------|--------|
| **Ordenação de eventos com buffer** | Documentado como TODO no ADR-004. Foco da Fase 5 foi dedup e persistência; buffer de 30s por máquina é melhoria planejada. |
| **Autenticação / Multi-tenant** | Não-objetivo da missão (§6). Walking skeleton é single-tenant por design. |
| **Integração com broker real** | O simulador cobre o escopo; migração para IoT Core documentada no ADR-009. |
| **UI polida / gráficos** | Dashboard prova a arquitetura (SSE + REST), não o design. Gráficos exigiram bibliotecas fora do escopo. |
| **Cobertura de código (coverage)** | pytest cobre unitários, integração, contratos e golden test; coverage tool não adiciona valor no momento. |
| **Alertas / Notificações** | Fora do escopo (§6). Sistema calcula OEE; alertas são camada acima. |

## Uso de IA (resumo - detalhes em docs/AI_ASSISTED.md)

**Ferramenta:** Claude Code (CLI) — deepseek-v4-pro.

**Como usei:**
- Especificação de cada fase (brainstorming → plan.md, requirements.md, validation.md)
- Implementação completa (TG por TG, commit por unidade lógica)
- Correção de bugs (healthchecks CI, uv.lock gitignored, dedup conflito de dados)
- Geração de documentação (ARQUITETURA.md, TRADEOFFS.md, ADRs, README)

**Onde discordei/corrigi a IA:**
- `[build-system]` prematuro na Fase 0 (quebrou build sem `src/oee_textil/`)
- `Annotated[Union]` não instanciável em Python 3.14 + Pydantic v2 (corrigido com `TypeAdapter`)
- Campo `schema` shadowing `BaseModel` (corrigido com `protected_namespaces`)
- Healthcheck do Mosquitto no CI usava `$SYS` topics (desabilitados no Mosquitto 2.x)
- `uv.lock` e `mosquitto.conf` estavam gitignored (quebravam build-and-smoke no CI)
- Dedup tests conflitavam com dados do consumidor rodando (corrigido com timestamps únicos)
- CloudWatch Logs ausentes do esboço Terraform (documentado como TODO)

**Registro completo:** [`docs/AI_ASSISTED.md`](docs/AI_ASSISTED.md) — decisões (D1–D5 por fase) + correções + prompts.
