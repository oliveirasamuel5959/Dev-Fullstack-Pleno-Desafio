# Requirements — Fase 9: CI/CD

> Feature derivada de [`../../specs/roadmap.md`](../../specs/roadmap.md) — Fase 9.
> Branch de trabalho: `desafio/samuel-oliveira`.

## 1. Contexto

Fases 0-8 estão entregues. Os quality gates do harness (`ruff check`, `ruff format --check`, `mypy`, `pytest`) já passam localmente com `uv run`, e o `docker compose up -d` sobe mosquitto + timescaledb + consumidor com healthchecks saudáveis. O que falta é automatizar esses gates em pipeline real — exigência do eixo CI/CD da avaliação.

**Gate de saída:** push na branch dispara workflow GitHub Actions; pipeline inteiro verde.

## 2. Escopo

### Dentro

- **Workflow único** (`.github/workflows/ci.yml`) com 4 jobs:
  - `lint`: ruff check + ruff format --check
  - `typecheck`: mypy
  - `test`: pytest (com services mosquitto + timescaledb)
  - `build-and-smoke`: build da imagem Docker + compose up + healthcheck + compose down
- **Triggers**: `push` em `desafio/samuel-oliveira` + `pull_request` contra `main`
- **Actions oficiais**: `checkout`, `setup-python`, `setup-uv`
- **ADR-008**: CI/CD — GitHub Actions, estrutura do pipeline, decisões

### Fora

- Badges de status no README
- Cache de dependências (`uv` ou pip)
- Matrix build (múltiplas versões de Python)
- Deploy automatizado
- Cobertura de código (coverage)
- Secrets ou variáveis de ambiente complexas
- Notificações (Slack, email)

## 3. Decisões

| Decisão | Por quê |
|---------|---------|
| GitHub Actions (não GitLab CI, CircleCI, etc.) | Nativo do repositório, zero infra extra, executor Linux gratuito suficiente para o walking skeleton |
| Jobs sequenciais com `needs` (não paralelos) | `test` depende de lint passar; `build-and-smoke` depende de test passar — queremos fail fast |
| `setup-uv` da Astral | Action oficial do ecossistema uv; caching built-in |
| Services do GitHub Actions para mosquitto+timescaledb no job `test` | pytest precisa de broker e banco reais; services do GHA evitam dependência externa |
| Sem matrix, sem cache explícito | YAGNI — o escopo é provar o gate, não otimizar pipeline |
