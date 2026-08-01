# Requirements — Fase 8: Mini-dashboard ao vivo

> Feature derivada de [`../../specs/roadmap.md`](../../specs/roadmap.md) — Fase 8.
> Branch de trabalho: `desafio/samuel-oliveira`.

## 1. Contexto

O roadmap manda: **dar uma face visível ao esqueleto**. Hoje a API (Fase 7) expõe
dados de OEE, estado, Pareto e perdas via REST. O simulador (Fase 3) gera
tráfego contínuo. O que falta é uma interface que mostre esses dados atualizando
ao vivo, provando que o fluxo ponta a ponta funciona.

**Gate de saída:** com o simulador rodando, o dashboard atualiza ao vivo no
navegador.

## 2. Escopo

### Dentro

- **SSE endpoint** (`GET /api/v1/stream`) com estado + OEE a cada 2s
- **Página HTML estática** (`static/index.html`) servida pelo FastAPI
- **4 cards**: OEE atual, estado máquinas, Pareto, feed de eventos
- **JavaScript vanilla** com `EventSource` + `fetch`
- **CSS dark theme** sem frameworks externos
- **ADR-007**: SSE vs WebSocket/polling

### Fora

- Gráficos complexos (bibliotecas de chart)
- Autenticação/login
- Múltiplas páginas ou rotas de frontend
- Build de frontend (webpack/vite)
