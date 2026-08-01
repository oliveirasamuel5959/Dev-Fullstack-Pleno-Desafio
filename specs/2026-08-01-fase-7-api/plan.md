# Plan — Fase 7: API

> Execução de [requirements.md](requirements.md). Grupos de tarefas numerados.
> Critério de aceite final em [validation.md](validation.md).

## TG1 — Dependências + app FastAPI

- **1.1** `uv add fastapi uvicorn httpx`
- **1.2** Criar `src/oee_textil/routes/app.py`:
  - `app = FastAPI(...)`, lifespan, `get_db()` dependency
  - CORS middleware, prefixo `/api/v1`
- **1.3** Criar `src/oee_textil/schemas/api.py` com schemas de resposta
- **Verificação:** `make lint`; `uv run uvicorn oee_textil.routes.app:app` sobe
- **Commit:** `feat: FastAPI app + schemas de resposta + dependências (Fase 7)`

## TG2 — 5 routers + endpoints

- **2.1** `routes/oee.py`: `/oee/atual` + `/oee/serie`
- **2.2** `routes/paradas.py`: `/paradas/pareto`
- **2.3** `routes/estado.py`: `/estado/atual`
- **2.4** `routes/perdas.py`: `/perdas`
- **2.5** Registrar routers no `app.py`
- **Verificação:** `curl` cada endpoint retorna JSON válido
- **Commit:** `feat: 5 endpoints REST — OEE, perdas, Pareto, estado (Fase 7)`

## TG3 — Testes com TestClient

- **3.1** `tests/test_api.py` com `TestClient`
- **3.2** Testes unitários (mock session) + smoke (DB real)
- **Verificação:** `uv run pytest -k api -v` verde
- **Commit:** `test: API endpoints com TestClient (Fase 7)`

## TG4 — API no docker-compose + Makefile

- **4.1** Adicionar serviço `api` ao `docker-compose.yml`
- **4.2** Targets `api` e `api-logs` no Makefile
- **Verificação:** `docker compose up api` saudável; `curl localhost:8000/docs`
- **Commit:** `feat: serviço API no docker-compose + Makefile (Fase 7)`

## TG5 — ADR-006 + gates finais

- **5.1** `docs/adr/006-design-api-rest-fastapi.md`
- **5.2** Atualizar `docs/AI_ASSISTED.md`
- **5.3** Barra completa: `make lint && make test`
- **Commit:** `docs: ADR-006 API REST + registro AI_ASSISTED (Fase 7)` → push
