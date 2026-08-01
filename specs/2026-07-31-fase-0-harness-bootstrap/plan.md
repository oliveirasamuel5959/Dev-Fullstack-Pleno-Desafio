# Plan — Fase 0: Bootstrap do harness

> Execução de [requirements.md](requirements.md). Grupos de tarefas numerados,
> executados **em ordem**; cada grupo termina em verificação + commit próprio
> (D5). Critério de aceite final em [validation.md](validation.md).

## TG1 — Dependências e configuração do harness

- **1.1** `uv add --dev pytest ruff mypy pre-commit`
- **1.2** Configurar ruff no `pyproject.toml`: `target-version = "py314"`,
  `src = ["src"]`, `lint.select = ["E", "F", "I", "UP", "B", "SIM", "RUF"]`.
- **1.3** Configurar mypy no `pyproject.toml`: `strict = true`,
  `python_version = "3.14"`, `mypy_path = "src"`, `packages = ["oee_textil"]`.
- **1.4** Configurar pytest no `pyproject.toml`: `testpaths = ["tests"]`,
  `pythonpath = ["src"]`.
- **Verificação:** `uv run ruff check` e `uv run mypy` executam (mesmo que
  ainda sem código do pacote) sem erro de configuração.
- **Commit:** `chore: add harness dev-deps e config (ruff, mypy, pytest)`

## TG2 — Layout `src/` rigoroso + smoke test

- **2.1** Criar `src/oee_textil/` com `__init__.py` e os subpacotes `core/`,
  `models/`, `schemas/`, `repositories/`, `services/`, `routes/`, `simulador/`
  — cada um com `__init__.py` contendo **apenas** o docstring de propósito
  (conforme D3 em requirements.md).
- **2.2** Criar `src/oee_textil/main.py` (função `main()` anotada + guarda
  `__main__`), relocando o hello-world; **remover** o `main.py` da raiz.
- **2.3** Criar `tests/test_smoke.py`: importa `oee_textil` e cada subpacote;
  falha se qualquer um não importar.
- **Verificação:** `uv run python -m oee_textil` roda;
  `uv run pytest -v` verde; `uv run mypy` strict verde.
- **Commit:** `feat: estrutura src/oee_textil com fronteiras de responsabilidade`

## TG3 — ADR-001: monorepo + estilo arquitetural

- **3.1** Criar `docs/adr/001-monorepo-um-pacote-n-entry-points.md` a partir de
  `docs/adr/000-template.md`: Status **Aceito**, Data **2026-07-31**,
  Decisores **Samuel Oliveira**; contexto (eixo avaliado, tamanho do time,
  escopo de skeleton); decisão (D1); tabela de alternativas (workspace por
  serviço; monólito single-process; microsserviços multi-repo) com prós/contras
  e "por que não"; consequências incluindo dívidas assumidas e gatilho de
  reavaliação (extrair serviço quando houver dono/escala próprios).
- **Verificação:** ADR segue o template integralmente, sem seção vazia.
- **Commit:** `docs: ADR-001 monorepo, um pacote, N entry points`

## TG4 — Pre-commit

- **4.1** Criar `.pre-commit-config.yaml`: hook oficial `ruff` (lint com
  `--fix` + format) e hook `repo: local` de mypy rodando `uv run mypy`.
- **4.2** `uv run pre-commit install` e `uv run pre-commit run --all-files`.
- **Verificação:** run em todos os arquivos verde (corrigir o que aparecer).
- **Commit:** `chore: pre-commit com ruff e mypy`

## TG5 — Gates finais e registros

- **5.1** Rodar a barra completa: `uv run pytest`, `uv run ruff check`,
  `uv run ruff format --check`, `uv run mypy`.
- **5.2** Atualizar `docs/AI_ASSISTED.md`: entrada da Fase 0 (ferramentas
  usadas, onde a IA ajudou, onde foi corrigida/contraditada — seção 3 do
  template).
- **5.3** Atualizar `CLAUDE.md`: seção de toolchain passa a refletir as deps
  reais do `pyproject.toml` e o layout `src/oee_textil/`.
- **5.4** Executar o procedimento de [validation.md](validation.md) do início
  ao fim.
- **Commit:** `docs: registro AI_ASSISTED (Fase 0) e sync do CLAUDE.md` →
  push para `desafio/samuel-oliveira`.
