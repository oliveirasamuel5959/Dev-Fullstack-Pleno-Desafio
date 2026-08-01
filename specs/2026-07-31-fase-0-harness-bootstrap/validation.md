# Validation — Fase 0: Bootstrap do harness

> Procedimento executável de validação da Fase 0. Rode as verificações abaixo
> **na ordem** após executar todos os grupos de tarefas de [plan.md](plan.md).
> Referência de requisitos: [requirements.md](requirements.md).
> Critério de saída do [roadmap](../../specs/roadmap.md): `uv run pytest`,
> `uv run ruff check` e `uv run mypy` passam no scaffold.

---

## V1 — Configuração do harness (TG1)

- [ ] **1.1** `uv run ruff check` executa sem erro de configuração
  ```bash
  uv run ruff check
  ```
- [ ] **1.2** `uv run mypy` executa sem erro de configuração
  ```bash
  uv run mypy
  ```
- [ ] **1.3** `pyproject.toml` contém as seções de configuração:
  - `[tool.ruff]` com `target-version`, `src`, `lint.select`
  - `[tool.mypy]` com `strict = true`, `python_version`, `mypy_path`, `packages`
  - `[tool.pytest.ini_options]` com `testpaths`, `pythonpath`
- [ ] **1.4** Dev-deps aparecem em `[dependency-groups]` do `pyproject.toml`:
  `pytest`, `ruff`, `mypy`, `pre-commit`

---

## V2 — Layout `src/` e smoke test (TG2)

- [ ] **2.1** `src/oee_textil/` existe e contém:
  ```
  src/oee_textil/
  ├── __init__.py
  ├── main.py
  ├── core/__init__.py
  ├── models/__init__.py
  ├── schemas/__init__.py
  ├── repositories/__init__.py
  ├── services/__init__.py
  ├── routes/__init__.py
  └── simulador/__init__.py
  ```
- [ ] **2.2** Cada `__init__.py` contém **apenas** docstring descrevendo a
  responsabilidade do subpacote (sem código de domínio).
- [ ] **2.3** `main.py` da raiz **não existe** (foi removido).
  ```bash
  test ! -f main.py && echo "OK: main.py raiz removido"
  ```
- [ ] **2.4** `uv run python -m oee_textil` executa e imprime o hello-world.
- [ ] **2.5** `tests/test_smoke.py` existe e importa `oee_textil` e todos os
  subpacotes.
- [ ] **2.6** `uv run pytest -v` passa (smoke test verde).
- [ ] **2.7** `uv run mypy` strict passa sem erros.

---

## V3 — ADR-001: monorepo + estilo arquitetural (TG3)

- [ ] **3.1** `docs/adr/001-monorepo-um-pacote-n-entry-points.md` existe.
- [ ] **3.2** Segue integralmente `docs/adr/000-template.md`:
  - Status: **Aceito**
  - Data: **2026-07-31**
  - Decisores: **Samuel Oliveira**
- [ ] **3.3** Seção _Contexto_ descreve o problema e restrições.
- [ ] **3.4** Seção _Decisão_ declara D1 (ver `requirements.md`) de forma direta.
- [ ] **3.5** Tabela de _Alternativas consideradas_ tem pelo menos 3 entradas
  (workspace por serviço, monólito single-process, microsserviços multi-repo),
  cada uma com prós, contras e "por que não".
- [ ] **3.6** Seção _Consequências_ inclui:
  - Positivas
  - Negativas / dívidas assumidas
  - Gatilho de reavaliação (quando extrair serviço)

---

## V4 — Pre-commit (TG4)

- [ ] **4.1** `.pre-commit-config.yaml` existe e contém:
  - Hook oficial `ruff` (lint com `--fix` + format)
  - Hook `repo: local` de `mypy` (`entry: uv run mypy`)
- [ ] **4.2** `uv run pre-commit run --all-files` passa em todos os hooks.
  ```bash
  uv run pre-commit run --all-files
  ```

---

## V5 — Barra completa e registros (TG5)

- [ ] **5.1** `uv run pytest` verde (sem falhas).
- [ ] **5.2** `uv run ruff check` verde (sem erros de lint).
- [ ] **5.3** `uv run ruff format --check` verde (sem diffs de formatação).
- [ ] **5.4** `uv run mypy` verde (strict, zero erros).
- [ ] **5.5** `docs/AI_ASSISTED.md` tem entrada da Fase 0 preenchida (seções:
  ferramentas usadas, contribuição da IA, correções/contradições).
- [ ] **5.6** `CLAUDE.md` reflete as dependências reais e o layout
  `src/oee_textil/` (seção de toolchain atualizada).

### Comando único da barra

```bash
uv run ruff check && \
  uv run ruff format --check && \
  uv run mypy && \
  uv run pytest -v && \
  echo "FASE 0: TODOS OS GATES VERDES"
```

---

## Resumo

| Verificação | Descrição | Resultado |
|-------------|-----------|-----------|
| V1 | Configuração do harness | ✅ / ❌ |
| V2 | Layout `src/` e smoke test | ✅ / ❌ |
| V3 | ADR-001 | ✅ / ❌ |
| V4 | Pre-commit | ✅ / ❌ |
| V5 | Barra completa e registros | ✅ / ❌ |

> **Fase 0 fechada quando:** todas as verificações V1–V5 = ✅.
> Só então a Fase 1 pode ser aberta (regra 1 do roadmap).
