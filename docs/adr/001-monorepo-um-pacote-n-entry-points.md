# ADR-001: Monorepo, um pacote, N entry points

- **Status:** Aceito
- **Data:** 2026-07-31
- **Decisores:** Samuel Oliveira

## Contexto

O desafio avalia explicitamente o eixo "Monorepo vs. Microsserviços"
([ENTREGAVEIS.md](../../docs/ENTREGAVEIS.md) §3). O sistema tem ao menos 5
responsabilidades de runtime distintas (consumidor MQTT, motor de OEE, API HTTP,
simulador/publisher, dashboard SSE), mas o time é de **1 pessoa** e o escopo é
um **_walking skeleton_**, não um produto de produção. A escolha da organização
do código-fonte e da estratégia de deploy tem impacto direto em:

- Velocidade de iteração (feedback loop do harness)
- Coerência entre a decisão documentada e o código entregue
- Facilidade de reprodução (`docker compose up` único)

Restrições: Python 3.14 + uv (stack fixada em
[tech-stack.md](../../specs/tech-stack.md)); entrega como repositório público
único; Docker Compose como orquestrador local.

## Decisão

**Monorepo único com um pacote Python (`src/oee_textil/`) e N entry points
independentes**, cada um executado como um processo separado no Docker Compose.

O pacote é organizado por **fronteira de responsabilidade** (subpacotes `core/`,
`models/`, `schemas/`, `repositories/`, `services/`, `routes/`, `simulador/`),
não por tipo de runtime. Cada entry point importa o que precisa do pacote comum
e é invocado como um serviço isolado no `docker-compose.yml`:

| Serviço | Entry point |
|---------|-------------|
| `api` | `uv run uvicorn oee_textil.routes.app:app` |
| `consumidor` | `uv run python -m oee_textil.services.consumidor` |
| `simulador` | `uv run python -m oee_textil.simulador.publisher` |

Uma única imagem de container é construída; o Compose a reutiliza com comandos
diferentes.

## Alternativas consideradas

| Alternativa | Prós | Contras | Por que não |
|-------------|------|---------|-------------|
| **A — uv workspace com pacote por serviço** (`packages/api/`, `packages/consumidor/`, etc.) | Isolamento forte de dependências por serviço; cada um poderia ter seu próprio `pyproject.toml` | Cerimônia de build: múltiplos `pyproject.toml`, locks独立, complexidade de CI para resolver o workspace | O skeleton tem ~5 dependências compartilhadas (SQLAlchemy, Pydantic, aiomqtt); o isolamento não compensa a cerimônia. Só se justificaria com times separados ou dependências conflitantes. |
| **B — Monólito single-process** (consumidor MQTT como background task dentro do FastAPI) | Um processo para gerenciar; deploy trivial | Acopla ciclos de vida: se o consumidor cair, o FastAPI cai junto (ou vice-versa); backpressure do MQTT compete com threads do HTTP; enfraquece a narrativa _event-driven_ que é o coração do eixo 2 da avaliação | O desafio pede uma arquitetura event-driven com MQTT real (Mosquitto). Rodar o consumidor como tarefa assíncrona dentro do FastAPI esconde a separação produtor/consumidor que o broker proporciona. |
| **C — Microsserviços multi-repo** (um repo por serviço) | Isolamento total: CI, deploy e escala independentes por serviço | Overhead de coordenação entre repos (versionamento de contrato, PRs跨-repo, CI duplicado); complexidade desproporcional para 1 pessoa e um skeleton | Só se justifica com múltiplos times, cadências de deploy independentes e escala organizacional — nenhum desses fatores está presente no desafio. |

## Consequências

- **Positivas:**
  - Um único `pyproject.toml` e `uv.lock` → um comando instala tudo; feedback loop instantâneo.
  - CI simples: uma pipeline, um conjunto de gates (ruff → mypy → pytest) para todo o código.
  - Coerência com a avaliação: a decisão está documentada, o código reflete a decisão, o ADR é a evidência do eixo 3.
  - Fácil de "graduar" um serviço para repo próprio no futuro: a fronteira já existe como subpacote; basta extraí-lo com seu `pyproject.toml`.

- **Negativas / dívidas assumidas:**
  - Acoplamento de build: todos os serviços compartilham o mesmo `pyproject.toml` — uma dependência adicionada para a API está disponível para o consumidor (e vice-versa). Mitigação: revisão de código e a disciplina dos subpacotes (um módulo não deve importar de outro fora de sua responsabilidade).
  - O container único carrega dependências que nem todo serviço usa (ex.: `uvicorn` está na imagem do consumidor). Mitigação: para o skeleton isso é irrelevante; em produção, multi-stage builds ou imagens por entry point resolveriam.
  - Não há versionamento independente de serviços — um breaking change no schema força re-deploy de tudo.

- **Como reavaliar no futuro:**
  - Quando um serviço tiver **dono, cadência de deploy e escala próprios** (ex.: o motor de OEE passa a ser mantido por um time de dados com deploy semanal, enquanto a API é mantida pelo time de produto com deploy contínuo) → extrair para repo/próprio com `pyproject.toml`独立.
  - Gatilho concreto: o primeiro incidente em que um deploy da API quebrou o consumidor (ou vice-versa) por acoplamento de dependência → reabrir este ADR.
