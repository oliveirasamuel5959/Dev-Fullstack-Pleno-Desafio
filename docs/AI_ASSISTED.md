# Desenvolvimento Assistido por IA, Harness e Otimização de Contexto

Este eixo é **parte central** da avaliação. Queremos entender como você usa IA de
forma **profissional e rastreável**, não apenas como autocomplete. Preencha as
seções abaixo no seu fork.

---

## 1. O que é "Harness" aqui

_Harness_ é o conjunto de mecanismos que **prendem a IA (e o humano) ao trilho da
qualidade**: testes automatizados, _linters_, _type checkers_, _contract tests_,
_self-checks_, _pre-commit hooks_ e _quality gates_ de CI. Eles garantem que
código gerado (por você ou por IA) só entra se **passar em verificações
objetivas**.

Esperamos ver **pelo menos um mecanismo de harness real e executável** no repo
(ex.: um `pytest`/`vitest`/`go test` que roda, um _linter_ configurado, um
_contract test_ de schema MQTT, ou um _self-check_ do cálculo de OEE).

---

## 2. Otimização de contexto

Ferramentas de IA rendem mais quando o repositório é **legível para máquinas**.
Demonstre isso com artefatos como:

- `AGENTS.md` / `.github/copilot-instructions.md` - convenções, comandos, arquitetura.
- `CONVENTIONS.md` - padrões de código, nomenclatura, _boundaries_.
- Prompts versionados (ex.: `prompts/` ou `.prompts/`) para tarefas repetíveis.
- Documentação estruturada e _links_ cruzados (como este repositório).
- READMEs por módulo/serviço que explicam propósito e contratos.

> Objetivo: um agente de IA (ou um novo dev) deveria conseguir **se orientar
> sozinho** no seu projeto.

---

## 3. Preencha: Registro de uso de IA

> Substitua os exemplos pelo seu registro real. Seja honesto: usar IA **bem** é
> um diferencial positivo.

### 3.1 Ferramentas utilizadas
| Ferramenta | Para quê usei | Modelo/versão (se souber) |
|------------|---------------|---------------------------|
| Claude Code (CLI) | Especificação e implementação completa da Fase 0: configuração do harness (ruff, mypy, pytest), layout `src/oee_textil/`, ADR-001, pre-commit, smoke test | deepseek-v4-pro (via API compatível) |
| Claude Code (CLI) | Geração dos arquivos de spec (`plan.md`, `requirements.md`, `validation.md`) e documentação da Fase 0 | deepseek-v4-pro |

### 3.2 Decisões em que a IA ajudou - e onde eu discordei dela

- **Fase 0 — Estrutura do plano**: A IA propôs 5 task groups com verificação por grupo, o que fez sentido. Concordei com a estrutura e segui.
- **D1 (monorepo)**: A IA propôs monorepo com um pacote e N entry points; a justificativa de "um container, comandos diferentes" é pragmática e alinhada com o escopo de skeleton — concordei.
- **Fase 0 — backfill do validation.md**: A IA notou que `validation.md` estava referenciado mas não existia. Concordei em criá-lo antes de abrir a Fase 1, seguindo a regra do roadmap ("uma fase por vez").

### 3.3 O que eu revisei/corrigi no que a IA gerou

- **`[build-system]` prematuro**: A IA adicionou `[build-system]` com hatchling no TG1, mas o build quebrou porque `src/oee_textil/` ainda não existia. Corrigi: movi o `[build-system]` para o TG2, quando o pacote já existe.
- **`__main__.py` faltando**: `python -m oee_textil` falhou porque o pacote não tinha `__main__.py`. A IA não previu isso no plano inicial; adicionei o arquivo e corrigi o smoke test.
- **ruff format**: Vários arquivos gerados pela IA falharam `ruff format --check` (docstrings com trailing whitespace, falta de blank line após imports). O ruff fixou automaticamente; a lição é rodar o formatador antes de commitar, não depois.

### 3.4 Como otimizei o repositório para IA

- **CLAUDE.md**: Criado com regras não negociáveis, toolchain, convenções e referências cruzadas — o agente de IA lê isso no início de cada sessão e age conforme.
- **specs/ (mission.md, roadmap.md, tech-stack.md)**: Constituição do projeto em markdown estruturado, com links entre si — a IA consegue navegar e entender o contexto completo sem ajuda humana.
- **Planos por fase**: Cada feature spec (`plan.md`, `requirements.md`, `validation.md`) é autocontida e executável — a IA entra na fase, lê os 3 arquivos, e implementa.

### 3.5 Prompts relevantes (opcional, mas valorizado)

- **Prompt de criação da Fase 0**: "Find the next Fase on specs/roadmap.md and make a branch... Create a new directory YYYY-MM-DD-feature-name under specs..." — este prompt gerou todo o spec da Fase 0 (plan.md, requirements.md) com decisões travadas (D1–D5) alinhadas ao roadmap e à stack.
- **Prompt de implementação**: "Vamos implementar a Fase 0" — a IA leu plan.md, executou cada TG em ordem, verificou gates entre grupos, e committou um por TG. O resultado foi 4 commits atômicos com mensagens em português.

---

## 4. Como isso é avaliado (objetivo)

| Sub-critério | Atende quando... |
|--------------|------------------|
| Harness executável presente | Há teste/linter/contract-test que roda e falha se algo quebra |
| Uso de IA documentado | `AI_ASSISTED.md` preenchido com decisões e revisões reais |
| Otimização de contexto | Existe ≥1 artefato (AGENTS.md/instructions/prompts) útil e coerente |
| Pensamento crítico sobre IA | Há ao menos um caso em que o candidato **discordou/corrigiu** a IA |
