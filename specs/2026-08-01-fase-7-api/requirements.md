# Requirements — Fase 7: API

> Feature derivada de [`../../specs/roadmap.md`](../../specs/roadmap.md) — Fase 7.
> Branch de trabalho: `desafio/samuel-oliveira`.

## 1. Contexto

O roadmap manda: **responder às 4 perguntas do dashboard via HTTP**. Hoje o
repositório tem o motor de OEE (Fase 6) com funções puras, repository layer e
tabela `oee_agregado`. A Fase 7 expõe esses dados como API REST usando FastAPI,
com OpenAPI gerada automaticamente, testes com TestClient e o serviço `api`
integrado ao docker-compose.

**Gate de saída:** `uv run pytest -k api` verde.

## 2. Escopo

### Dentro

- **FastAPI + uvicorn + httpx**: `uv add fastapi uvicorn httpx`
- **App principal** (`src/oee_textil/routes/app.py`):
  - `FastAPI(title="OEE Têxtil API", version="0.1.0")`
  - Lifespan para logging de startup/shutdown
  - Dependency `get_db()` → `SessionLocal` por request com finally
  - CORS middleware (origem `*` para dev)
  - Prefixo `/api/v1` para versionamento
- **5 endpoints REST**:
  - `GET /api/v1/oee/atual` — OEE atual por máquina/linha/galpão (query params)
  - `GET /api/v1/oee/serie` — série temporal de OEE (máquina + janela)
  - `GET /api/v1/perdas` — análise de perdas D/P/Q
  - `GET /api/v1/paradas/pareto` — Pareto de motivos de parada
  - `GET /api/v1/estado/atual` — máquinas paradas/anômalas agora
- **Schemas de resposta Pydantic** (`src/oee_textil/schemas/api.py`):
  - `OeeResponse`, `OeeSerieItem`, `PerdasResponse`, `ParetoItem`, `EstadoItem`
- **Testes** (`tests/test_api.py`):
  - `TestClient` do FastAPI
  - Testes unitários (com mock de session) e smoke (com DB real)
- **docker-compose**: serviço `api` na porta 8000 com a mesma imagem Dockerfile
- **Makefile**: target `api` (sobe API) + `api-logs`
- **ADR-006**: design da API REST (FastAPI, OpenAPI, estrutura de routers)

### Fora (explicitamente)

- Dashboard HTML/SSE (Fase 8)
- Autenticação/authorização (fora do escopo do walking skeleton)
- Métodos POST/PUT/DELETE (API somente leitura)
- Paginação (volume de dados do skeleton não justifica)

## 3. Decisões travadas

### D1 — FastAPI com routers modulares

Cada grupo de endpoints é um `APIRouter` em arquivo separado (`oee.py`,
`paradas.py`, `estado.py`, `perdas.py`). Registrados no `app.py` com
prefixo `/api/v1`. Separação limpa, testável individualmente.

### D2 — Dependency injection para sessão DB

`get_db()` como generator dependency: cria `SessionLocal`, yields, fecha
no finally. Cada request recebe uma sessão limpa. Sem sessão global ou
thread-local.

### D3 — Schemas Pydantic de resposta (não reutilizar modelos ORM)

Os schemas de request/response são Pydantic models separados em
`schemas/api.py`. Não expor modelos SQLAlchemy diretamente na API
— a camada de serialização é explícita.

### D4 — Query params com defaults inteligentes

- `oee/atual`: sem parâmetros → OEE de todas as máquinas no turno atual
- `oee/serie`: default 24h se sem `inicio`/`fim`
- `paradas/pareto`: default turno atual
- `estado/atual`: sempre todas as máquinas

### D5 — API no docker-compose como serviço separado

Mesma imagem Dockerfile, comando diferente (`uvicorn`). Porta 8000 mapeada
para o host. Rede `oee-network` compartilhada com TimescaleDB.

## 4. Restrições

- Stack: FastAPI + uvicorn (tech-stack.md), httpx para TestClient
- Identificadores pt-BR nos schemas de resposta
- Testes das Fases 0–6 continuam verdes
- OpenAPI em `/docs` e `/redoc` (auto FastAPI)
