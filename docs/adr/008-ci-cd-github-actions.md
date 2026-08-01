# ADR-008: CI/CD com GitHub Actions

- **Status:** Aceito
- **Data:** 2026-08-01
- **Decisores:** Samuel Oliveira

## Contexto

O harness de qualidade (ruff, mypy, pytest, docker compose smoke) já é
executável localmente desde a Fase 0. As Fases 0–8 foram implementadas e
validadas manualmente a cada push. Para o eixo CI/CD da avaliação, é
necessário um pipeline que execute os mesmos gates de forma automatizada e
reprodutível a cada push e pull request.

Restrições:
- O repositório é público no GitHub — CI nativa (Actions) é gratuita.
- O walking skeleton é leve (~200 máquinas × 1 serviço Python) — um runner
  `ubuntu-latest` com containers de serviço é suficiente.
- Precisamos de broker MQTT e banco de dados reais para os testes de
  integração — mock não exercita os eixos Event-Driven e de dados da
  avaliação.

## Decisão

**Usar GitHub Actions com um workflow único (`ci.yml`), quatro jobs
sequenciais (`lint` → `typecheck` → `test` → `build-and-smoke`), usando
`astral-sh/setup-uv` para o toolchain Python e service containers nativos
do GHA para Mosquitto + TimescaleDB.**

Triggers: push na branch `desafio/samuel-oliveira` + pull_request contra
`main`.

A sequência é:
1. `lint` — ruff check + ruff format --check
2. `typecheck` — mypy strict mode
3. `test` — pytest completo (unitários + integração) com Mosquitto e
   TimescaleDB como service containers
4. `build-and-smoke` — build da imagem Docker, `docker compose up -d`,
   healthcheck de todos os serviços, `docker compose down`

Cada job depende do anterior (`needs`) para fail fast — não faz sentido
rodar testes se o código não passa no linter.

## Alternativas consideradas

| Alternativa | Prós | Contras | Por que não |
|-------------|------|---------|-------------|
| GitLab CI / CircleCI | Mais features (matrix, artifacts avançados) | Repositório é GitHub — exigiria mirror ou conta extra | Infra desnecessária para o escopo do desafio |
| Jobs totalmente paralelos | Mais rápido em wall-clock | `test` falharia por lint mesmo passando — tempo de runner desperdiçado | Fail fast é mais importante que velocidade |
| Mock de MQTT/DB nos testes | Não depende de service containers | Não exercita os eixos Event-Driven e Dados da avaliação | A avaliação pede exercício real de MQTT e séries temporais |
| `setup-python` + pip | Mais familiar | `uv` é mais rápido e já é o gerenciador do projeto; `astral-sh/setup-uv` é a action oficial | Manter coerência com o toolchain do projeto |
| Cache de dependências | Builds mais rápidos | Projeto tem ~15 deps; `uv sync` limpo leva <30s | YAGNI — otimização prematura para esta escala |
| Matrix build (Python 3.14+) | Testa compatibilidade futura | `requires-python = ">=3.14"` — só 3.14 existe hoje | Sem valor até que 3.15 exista |

## Consequências

- **Positivas:**
  - Pipeline verde = todos os gates passaram; feedback imediato em push e PR.
  - Service containers do GHA são efêmeros e isolados por execução — sem
    interferência entre runs.
  - Workflow único e simples — fácil de entender, modificar e estender.
  - `concurrency: cancel-in-progress` evita acúmulo de jobs em pushes
    rápidos consecutivos.

- **Negativas / dívidas assumidas:**
  - Sem cache de dependências — cada job faz `uv sync` do zero (~20-30s).
    Aceitável para o walking skeleton; reavaliar se o projeto crescer.
  - Sem matrix build — testamos apenas Python 3.14. Reavaliar quando 3.15
    for lançada ou se o projeto adotar múltiplas versões.
  - Service containers do GHA podem ter latência maior que Docker local;
    timeouts e healthcheck intervals são conservadores.

- **Como reavaliar no futuro:**
  - Se o `uv sync` começar a levar >1min, adicionar cache com
    `astral-sh/setup-uv` com `enable-cache: true`.
  - Se o projeto adotar Python 3.15+, adicionar matrix build.
  - Se o smoke test falhar por timeout, aumentar o `sleep` ou adicionar
    retry loop com `docker compose ps`.
