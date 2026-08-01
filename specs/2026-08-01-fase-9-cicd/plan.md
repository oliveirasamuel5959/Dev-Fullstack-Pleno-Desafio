# Plan — Fase 9: CI/CD

## TG1 — Workflow GitHub Actions

- Criar `.github/workflows/ci.yml` com 4 jobs sequenciais:
  - `lint`: `uv run ruff check` + `uv run ruff format --check`
  - `typecheck`: `uv run mypy`
  - `test`: `uv run pytest` (depende de `lint` + `typecheck`)
  - `build-and-smoke`: build Docker + `docker compose up -d` + healthchecks + `docker compose down` (depende de `test`)
- Triggers: `push` na branch `desafio/samuel-oliveira` + `pull_request` contra `main`
- Usar `actions/checkout@v4`, `actions/setup-python@v5`, `astral-sh/setup-uv@v5`
- Serviços de serviço (`services:`) para mosquitto + timescaledb no job de `test`

## TG2 — ADR-008

- `docs/adr/008-ci-cd-github-actions.md` seguindo o template `docs/adr/000-template.md`
- Conteúdo: justificativa de GitHub Actions, estrutura do pipeline, decisão YAGNI sem matrix/cache nesta fase

## TG3 — Documentação & AI log

- Atualizar `docs/DECISOES.md` com entrada sobre GitHub Actions
- Atualizar `docs/AI_ASSISTED.md` com log da Fase 9
