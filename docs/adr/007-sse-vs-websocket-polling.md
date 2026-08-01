# ADR-007: SSE vs WebSocket/Polling para o dashboard ao vivo

- **Status:** Aceito
- **Data:** 2026-08-01
- **Decisores:** Samuel Oliveira

## Contexto

A Fase 8 implementa o mini-dashboard ao vivo que exibe estado das máquinas e
OEE em tempo real. É necessário um mecanismo de comunicação servidor→cliente
para atualizações push. O tech-stack.md já indica SSE como escolha, mas o ADR
documenta a justificativa.

Restrições:
- Dashboard é somente-leitura (cliente não envia comandos)
- ~200 máquinas, atualização a cada 1–5s
- Frontend: HTML + JS vanilla, sem frameworks
- Servidor: FastAPI (async nativo, suporte a streaming)

## Decisão

### Server-Sent Events (SSE)

SSE é um padrão W3C sobre HTTP: o servidor mantém uma conexão aberta com
`Content-Type: text/event-stream` e envia eventos delimitados por `data:`.
O cliente usa a API `EventSource` (nativa em todos os navegadores) para
receber eventos com reconexão automática embutida.

**Implementação:**
- `GET /api/v1/stream` — `StreamingResponse` com `text/event-stream`
- Async generator envia JSON a cada 2s com estado + OEE
- `Cache-Control: no-cache`, `Connection: keep-alive`
- `EventSource` no frontend: reconexão automática em caso de queda

## Alternativas consideradas

| Alternativa | Por que não |
|-------------|-------------|
| **WebSocket** | Bidirecional — o dashboard é somente-leitura; ws requer upgrade de conexão e mais código no frontend/backend; SSE é mais simples e usa HTTP padrão |
| **Polling (setInterval + fetch)** | A cada 2s com ~200 máquinas = 100 req/s desperdiçados quando não há mudanças; SSE mantém uma conexão e só envia dados quando há eventos |
| **Long polling** | Complexidade similar ao SSE sem o benefício da API `EventSource` nativa |

## Consequências

**Positivas:**
- `EventSource` nativo no navegador — zero dependências JS
- Reconexão automática sem código adicional
- HTTP padrão — funciona através de proxies e load balancers
- Streaming nativo do FastAPI/Starlette

**Negativas:**
- Unidirecional (servidor→cliente) — suficiente para dashboard, mas limita
  interações futuras (ex.: clicar para detalhes usa REST)
- Máximo de ~6 conexões SSE por domínio em alguns navegadores (HTTP/1.1) —
  não é problema com 1 stream
- Sem suporte a binary frames — mas JSON é suficiente para este caso
