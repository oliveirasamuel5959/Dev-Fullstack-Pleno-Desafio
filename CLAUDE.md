# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

A **technical challenge (desafio) for a mid-level full-stack developer position**: design the software foundation for IoT (MQTT) data ingestion and an operational **OEE dashboard** for a textile factory ("Malharia Contínua S.A." — fictitious). The evaluation is on **architecture reasoning, not product completeness** — depth of justification beats volume of code. A *walking skeleton* that runs is sufficient; do **not** try to implement the whole system.

The full challenge brief is `README.md`; the binding rules are in `docs/` (see Deliverables below).

**Current state:** scaffold only. `main.py` is a hello-world; `docs/` still contains the challenge templates. The solution (architecture docs, ADRs, code) is what we are building.

## Language

Challenge docs are **pt-BR** — write all deliverable documentation (`docs/ARQUITETURA.md`, ADRs, `DECISOES.md`, etc.) in Portuguese to match the evaluation. Message/data contract field names are already established in Portuguese (`maquina_id`, `motivo_codigo`, `ts_sensor`, `unidades_produzidas`) — keep them as-is.

## Non-negotiable domain rules (source of truth: `docs/ESPECIFICACAO_TECNICA.md`)

- **OEE = Disponibilidade × Performance × Qualidade** — the *product*, never the average. `README.md` §4 presents a junior dev averaging the three factors as a mentoring trap; any code or doc computing OEE as a mean is wrong by definition.
  - Disponibilidade = Tempo Rodando / Tempo Planejado (planejado = turno − paradas **planejadas**)
  - Performance = (Tempo de Ciclo Ideal × Total Produzido) / Tempo Rodando
  - Qualidade = (produzidas − refugo) / produzidas
- Factors must be clamped to `[0, 1]`; inconsistent data must be flagged, not silently absorbed.
- Handle (or explicitly document handling of): **late-arriving events** after window close, **clock drift** (`ts_sensor` vs `ts_ingestao`), **duplicates/out-of-order** messages, **idempotency**, **backpressure**, **dead-letter** for invalid messages, **versioned message schemas** (`telemetria.v1`, `estado.v1`, `parada.v1`, `producao.v1`).
- The spec's conceptual scope may be extended but **never reduced**.
- `data/exemplos-mqtt/` contains **intentional defects** (duplicate events, out-of-order events, `rpm=0`) — they exist to exercise idempotency/ordering/stop-detection. Treating them (or documenting how) scores points; do not "clean" the fixture files.

## Deliverables expected (checklist: `docs/ENTREGAVEIS.md`)

- `docs/ARQUITETURA.md`, C4 diagrams (at least Context + Container, Mermaid ok), **≥3 ADRs** using `docs/adr/000-template.md`, `docs/DECISOES.md` (justify *every* stack choice), `docs/TRADEOFFS.md`.
- `docs/AI_ASSISTED.md` filled with the **real** AI-usage log — it must include at least one case where AI output was contradicted/corrected. Update it as work happens, not at the end.
- A **walking skeleton** (`docker compose up` or equivalent) **or** API contract (OpenAPI) + wireframe.
- **Harness**: at least one executable quality gate (pytest suite, configured linter, MQTT schema contract test, or OEE-calculation self-check). This is a graded axis, not optional.
- Where work stops consciously, leave explicit `TODO`s with rationale — valued by the evaluators.

## Toolchain

- **Python 3.14, managed by `uv`** (`pyproject.toml` + `uv.lock`; never edit `uv.lock` by hand):
  - `uv sync` — install deps into `.venv`
  - `uv add <pkg>` / `uv remove <pkg>` — manage dependencies
  - `uv run python -m oee_textil` — entry point; `uv run pytest` / `uv run pytest path/to/test_file.py::test_name` — tests / single test
  - `uv run ruff check` / `uv run ruff format` / `uv run mypy` — lint/format/typecheck
  - `uv run pre-commit run --all-files` — full pre-commit check
- **Build:** hatchling (`[build-system]` in `pyproject.toml`); package at `src/oee_textil/`
- **Installed dev-deps:** `pytest`, `ruff`, `mypy`, `pre-commit` (see `pyproject.toml` `[dependency-groups].dev`)
- `.claude/settings.json` pre-approves: **FastAPI/uvicorn, SQLAlchemy/Alembic, pytest, ruff, mypy, docker compose** — these aren't all in `pyproject.toml` yet; add them via `uv add` as they get used.
- **Pre-commit:** `.pre-commit-config.yaml` with ruff (official hook) + mypy (local hook via `uv run mypy`)

## Git workflow

Per the challenge rules: work happens on the candidate's fork, ideally on a branch `desafio/<nome>`; the final repo must be public with a readable commit history. The optional PR back to the original repo uses `.github/PULL_REQUEST_TEMPLATE.md`.

## Evaluation axes (what every change should serve)

Architecture & C4 modeling · Event-driven/MQTT design (topics, QoS, idempotency, backpressure) · monorepo-vs-microservices decision · cloud strategy · CI/CD with quality gates · AI-assisted dev + harness · correct OEE data modeling · overall coherence between decisions and code. When adding anything, ask: which axis does this strengthen, and is the *why* written down?
