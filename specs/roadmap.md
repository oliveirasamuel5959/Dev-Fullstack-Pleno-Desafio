# Roadmap

> Ordem de implementação em **fases muito pequenas**, _contracts-first_, com a
> documentação escrita **junto** de cada fase (nunca no final). Cada fase tem
> um **critério de saída executável** — uma fase só fecha com o seu gate do
> harness verde. Conformidade com [mission.md](mission.md) é pré-requisito de
> toda fase.

**Estratégia:** contratos antes de código de infraestrutura, porque o eixo
Event-Driven & MQTT é o coração da avaliação; os ADRs nascem no momento em que
a decisão é tomada (o roadmap rende ~6 ADRs; o mínimo exigido são 3).

---

## Fase 0 — Bootstrap do harness
**Objetivo:** quality gates rodando antes de qualquer código de domínio.
**Entregas:** `uv add --dev pytest ruff mypy`; config de ruff/mypy no
`pyproject.toml`; layout `src/`; **ADR-001: monorepo + estilo arquitetural**.
**Saída:** `uv run pytest`, `uv run ruff check` e `uv run mypy` passam no
scaffold.

## Fase 1 — Contratos de mensagem
**Objetivo:** os 4 schemas como código, não como prosa.
**Entregas:** modelos Pydantic de `telemetria.v1`, `estado.v1`, `parada.v1`,
`producao.v1`; export de JSON Schema para `docs/contracts/`; _contract test_
que valida cada linha de `data/exemplos-mqtt/*.ndjson`; **ADR-002:
versionamento de schema** (evolução aditiva, campo `schema`).
**Saída:** `uv run pytest -k contract` verde.

## Fase 2 — Infra local
**Objetivo:** broker e banco sobem com um comando.
**Entregas:** `docker-compose.yml` (mosquitto + timescaledb), configs e
healthchecks.
**Saída:** `docker compose up -d` sobe ambos; `docker compose ps` saudável.

## Fase 3 — Simulador / publisher
**Objetivo:** gerar tráfego MQTT real sem fábrica real.
**Entregas:** CLI que lê os NDJSON/CSV de exemplo e publica na topologia
`fabrica/{galpao}/{linha}/{maquina}/...`, com flags de velocidade e loop.
**Saída:** mensagens visíveis em `mosquitto_sub -t 'fabrica/#'`.

## Fase 4 — Modelo de dados
**Objetivo:** persistência coerente com o modelo conceitual da spec §3.
**Entregas:** modelos SQLAlchemy (catálogo de máquinas, hypertable de
telemetria, eventos de parada, produção, motivos, turnos); Alembic init +
primeira migração; seed dos CSVs.
**Saída:** `uv run alembic upgrade head` aplica limpo; tabelas populadas.

## Fase 5 — Consumidor de ingestão
**Objetivo:** a primeira fatia ponta a ponta, resistente aos defeitos
intencionais.
**Entregas:** assinante aiomqtt → validação (Fase 1) → **dedup/idempotência**
(constraint única) → ordenação → persistência; dead-letter para mensagens
inválidas; testes com fixtures (duplicata, fora de ordem, `rpm=0`);
**ADR-003: idempotência, ordenação e backpressure**.
**Saída:** simulador → broker → consumidor → banco funcionando; teste de dedup
verde.

## Fase 6 — Motor de OEE
**Objetivo:** o cálculo certo, provado com números do enunciado.
**Entregas:** funções puras de D/P/Q/OEE por máquina×janela; clamp `[0,1]`;
política de janela e eventos tardios; _golden self-check_ com o exemplo de
`docs/CONTEXTO_NEGOCIO.md` §2; **ADR-004: janelas de agregação e late
events**.
**Saída:** `uv run pytest -k oee` verde (inclui o caso dourado ≈ 0,79).

## Fase 7 — API
**Objetivo:** responder às 4 perguntas do dashboard via HTTP.
**Entregas:** endpoints de OEE atual (máquina/linha/galpão), Pareto de
paradas, série temporal e estado ao vivo; OpenAPI gerada; testes com
`TestClient`.
**Saída:** `uv run pytest -k api` verde.

## Fase 8 — Mini-dashboard ao vivo
**Objetivo:** dar uma face visível ao esqueleto (spec §5, opção A).
**Entregas:** página HTML + JS vanilla servida pelo FastAPI; stream SSE com
estado e OEE de uma máquina/linha; **ADR-005: SSE vs WebSocket/polling**.
**Saída:** com o simulador rodando, o dashboard atualiza ao vivo no navegador.

## Fase 9 — CI/CD
**Objetivo:** os gates do harness executando em pipeline real.
**Entregas:** workflow GitHub Actions (ruff → mypy → pytest → build → smoke do
compose).
**Saída:** pipeline verde em push.

## Fase 10 — Documentação final & nuvem
**Objetivo:** fechar todos os entregáveis documentais.
**Entregas:** `docs/ARQUITETURA.md` com C4 Contexto + Contêiner (Mermaid);
design de deploy em nuvem + **ADR-006: estratégia de nuvem**;
`docs/DECISOES.md`; `docs/TRADEOFFS.md`; README do fork (como rodar, o que
entregou, o que ficou de fora e por quê); fechamento de
`docs/AI_ASSISTED.md`.
**Saída:** checklist de `docs/ENTREGAVEIS.md` integralmente marcado.

---

## Regras do roadmap

1. **Uma fase por vez.** Não abrir a fase N+1 com o gate da N vermelho.
2. Fases podem ser fatiadas ainda mais na execução — nunca fundidas.
3. Descobertas que mudam decisões anteriores → ADR novo ou atualização do
   existente, nunca edição silenciosa.
4. `docs/AI_ASSISTED.md` é atualizado **ao fim de cada fase** (o que a IA fez,
   onde foi corrigida).
