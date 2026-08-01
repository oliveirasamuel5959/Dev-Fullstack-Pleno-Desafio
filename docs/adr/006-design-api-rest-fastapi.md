# ADR-006: Design da API REST com FastAPI e OpenAPI

- **Status:** Aceito
- **Data:** 2026-08-01
- **Decisores:** Samuel Oliveira

## Contexto

A Fase 7 expõe os dados de OEE via API REST HTTP para responder às 5 perguntas
do dashboard operacional (CONTEXTO_NEGOCIO.md §4). É necessário decidir o
framework, a estrutura de rotas, o formato de respostas e a estratégia de
testes.

Restrições:
- Stack já fixada em Python 3.14 + FastAPI (tech-stack.md)
- OEE já calculado (Fase 6) com funções puras e repository layer
- Dados persistidos em TimescaleDB (Fase 4) com tabela `oee_agregado`
- API somente leitura (GET) para o walking skeleton
- OpenAPI deve ser gerada automaticamente (entregável da spec §5)
- Testes com `TestClient` (gate: `pytest -k api`)

## Decisão

### 1. FastAPI com routers modulares

FastAPI é o framework definido no tech-stack.md. A estrutura usa:
- `routes/app.py`: instância `FastAPI`, lifespan, CORS, dependency `get_db()`
- `routes/oee.py`, `paradas.py`, `estado.py`, `perdas.py`: `APIRouter` cada
- Todos registrados com prefixo `/api/v1` para versionamento
- OpenAPI em `/docs` (Swagger) e `/redoc` (ReDoc) — automático

### 2. Dependency injection para sessão DB

`get_db()` como generator dependency FastAPI: cria `SessionLocal`, yields,
fecha no finally. Cada request recebe uma sessão limpa, sem estado global.
Segue o mesmo padrão de `SessionLocal` definido em `core/database.py` (Fase 4).

### 3. Schemas Pydantic de resposta separados dos modelos ORM

`schemas/api.py` define modelos de resposta (`OeeResponse`, `ParetoItem`,
`EstadoItem`, etc.) independentes dos modelos SQLAlchemy. A serialização
é explícita — a API não expõe colunas do banco diretamente.

### 4. API como serviço no docker-compose

Mesma imagem Dockerfile (ADR-001: "um container, comandos diferentes"),
comando `uvicorn`. Porta 8000 mapeada. Rede `oee-network` compartilhada
com TimescaleDB. Sem dependência do Mosquitto (API só consulta o banco).

### 5. Testes com TestClient (httpx)

`fastapi.testclient.TestClient` (baseado em httpx) para testes síncronos.
Marcados com `-k api`. Testes unitários (sem DB) e smoke (com DB real,
`@pytest.mark.smoke`).

### 6. CORS aberto para desenvolvimento

`allow_origins=["*"]`, somente GET. O dashboard (Fase 8) é servido como
página estática pelo próprio FastAPI ou em outro servidor local.

## Alternativas consideradas

| Alternativa | Por que não |
|-------------|-------------|
| Flask + flask-restx | FastAPI já é a escolha do tech-stack; OpenAPI nativa, async, Pydantic integrado |
| GraphQL (Strawberry) | Overkill para 5 endpoints GET; REST é suficiente |
| Router único (monolítico) | Routers modulares facilitam testes e manutenção |
| Expor modelos ORM diretamente | Vazamento de schema interno; serialização explícita é mais segura |
| API sem containerização | Consistência com o resto da stack (consumidor, simulador) |

## Consequências

**Positivas:**
- OpenAPI gerada automaticamente → documentação sempre atualizada
- Routers modulares → cada grupo testável isoladamente
- Mesma imagem Docker → consistência com ADR-001
- TestClient → testes rápidos sem servidor real

**Negativas:**
- API somente leitura → sem endpoints de configuração ou trigger de recálculo
- Sem paginação → volume do skeleton não justifica
- CORS `*` → inseguro para produção (aceitável para walking skeleton)
