# Validation — Fase 7: API

> Critério de saída: `uv run pytest -k api` verde.

---

## V1 — Dependências + app (TG1)

- [ ] **1.1** `fastapi`, `uvicorn`, `httpx` em `pyproject.toml`
- [ ] **1.2** `uv run uvicorn oee_textil.routes.app:app` sobe sem erro
- [ ] **1.3** `curl http://localhost:8000/docs` retorna OpenAPI JSON
- [ ] **1.4** `make lint` verde

## V2 — Endpoints (TG2)

- [ ] **2.1** `GET /api/v1/oee/atual?maquina_id=TEAR-G1-L2-07` → 200 JSON
- [ ] **2.2** `GET /api/v1/oee/serie?maquina_id=TEAR-G1-L2-07` → 200 JSON
- [ ] **2.3** `GET /api/v1/perdas?maquina_id=TEAR-G1-L2-07` → 200 JSON
- [ ] **2.4** `GET /api/v1/paradas/pareto` → 200 JSON
- [ ] **2.5** `GET /api/v1/estado/atual` → 200 JSON

## V3 — TestClient (TG3)

- [ ] **3.1** `uv run pytest -k api -v` verde
- [ ] **3.2** Testa 200, 404, 422 (validação)

## V4 — Docker (TG4)

- [ ] **4.1** `docker compose up api` saudável
- [ ] **4.2** `curl localhost:8000/docs` acessível

## V5 — Gates (TG5)

- [ ] **5.1** `make lint && make test` verde
- [ ] **5.2** `docs/adr/006-design-api-rest-fastapi.md` existe
- [ ] **5.3** Fases 0–6 sem regressão

---

## Fluxo completo

```bash
make lint && make test
uv run pytest -k api -v
curl http://localhost:8000/docs
curl http://localhost:8000/api/v1/oee/atual?maquina_id=TEAR-G1-L2-07
```

## Resumo

| V | Descrição | Resultado |
|----|-----------|-----------|
| V1 | Dependências + app FastAPI | ✅ / ❌ |
| V2 | 5 endpoints REST | ✅ / ❌ |
| V3 | TestClient (pytest -k api) | ✅ / ❌ |
| V4 | Docker compose API service | ✅ / ❌ |
| V5 | Gates + ADR-006 | ✅ / ❌ |
