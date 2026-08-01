# Validation — Fase 9: CI/CD

> Como saber que a implementação deu certo e pode ser mergeada.

## Gate executável (saída da Fase)

Push na branch `desafio/samuel-oliveira` dispara o workflow `ci.yml` no GitHub Actions. **Pipeline inteiro verde** nos 4 jobs:

```
lint (ruff) → typecheck (mypy) → test (pytest) → build-and-smoke (docker compose)
```

## Critérios de merge

### 1. Lint passa (0 erros)

```bash
uv run ruff check        # 0 errors, 0 warnings
uv run ruff format --check  # 0 files would be reformatted
```

### 2. Typecheck passa (0 erros)

```bash
uv run mypy              # Success: no issues found
```

### 3. Testes passam (todos verdes)

```bash
uv run pytest            # All tests passing, 0 failures
```

### 4. Build & smoke do compose passa

```bash
docker compose build consumidor   # Build sem erros
docker compose up -d              # Serviços sobem
docker compose ps                 # Todos healthy
docker compose down               # Limpeza sem erros
```

### 5. ADR-008 existe e segue o template

- `docs/adr/008-ci-cd-github-actions.md` criado
- Segue estrutura de `docs/adr/000-template.md` (título, status, contexto, decisão, consequências)
- Justifica GitHub Actions e estrutura do pipeline

### 6. Documentação atualizada

- `docs/DECISOES.md` contém entrada sobre GitHub Actions
- `docs/AI_ASSISTED.md` contém log da Fase 9

## Evidência

- Link ou screenshot do workflow verde no GitHub Actions (aba "Actions" do repositório)
- Output dos 4 jobs visível e sem erros
