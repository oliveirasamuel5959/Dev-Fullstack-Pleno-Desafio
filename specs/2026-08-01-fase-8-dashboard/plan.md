# Plan — Fase 8: Mini-dashboard ao vivo

## TG1 — SSE endpoint

- Criar `routes/stream.py` com `GET /api/v1/stream`
- `StreamingResponse` com `text/event-stream`
- Envia estado máquinas + OEE a cada 2s via `asyncio.sleep`
- Registrar no `app.py`

## TG2 — Dashboard HTML

- Criar `static/index.html` com 4 cards + CSS dark + JS vanilla
- Montar static files no FastAPI (`app.mount("/", ...)`)
- `EventSource` para SSE + `fetch` para dados iniciais

## TG3 — ADR-007 + gates

- `docs/adr/007-sse-vs-websocket-polling.md`
- Atualizar `docs/AI_ASSISTED.md`
- Barra completa: `make lint && make test`
