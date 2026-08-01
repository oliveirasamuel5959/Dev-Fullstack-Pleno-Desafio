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
| Claude Code (CLI) | Implementação completa da Fase 1: modelos Pydantic (4 schemas + union), JSON Schema export, contract tests, ADR-002 | deepseek-v4-pro |
| Claude Code (CLI) | Especificação e implementação completa da Fase 2: docker-compose (mosquitto + timescaledb), smoke tests de conectividade, Makefile | deepseek-v4-pro |
| Claude Code (CLI) | Especificação e implementação completa da Fase 3: simulador MQTT (CLI argparse), leitor de NDJSON/CSV, publicador na topologia fabrica/... | deepseek-v4-pro |

### 3.2 Decisões em que a IA ajudou - e onde eu discordei dela

- **Fase 0 — Estrutura do plano**: A IA propôs 5 task groups com verificação por grupo, o que fez sentido. Concordei com a estrutura e segui.
- **D1 (monorepo)**: A IA propôs monorepo com um pacote e N entry points; a justificativa de "um container, comandos diferentes" é pragmática e alinhada com o escopo de skeleton — concordei.
- **Fase 0 — backfill do validation.md**: A IA notou que `validation.md` estava referenciado mas não existia. Concordei em criá-lo antes de abrir a Fase 1, seguindo a regra do roadmap ("uma fase por vez").
- **Fase 1 — D1 (Pydantic + discriminated union)**: A IA propôs usar `Annotated[Union[...], Field(discriminator="schema")]` com `TypeAdapter` do Pydantic v2. Concordei — resolve o despacho sem if/elif manual.
- **Fase 1 — D3 (contract test valida todas as linhas)**: A IA propôs que os defeitos intencionais (`rpm=0`, duplicata, fora de ordem) são schema-valid e não devem ser rejeitados. Concordei — o tratamento é responsabilidade do consumidor (Fase 5), não dos schemas.
- **Fase 2 — D1 (Mosquitto anônimo)**: A IA propôs Mosquitto sem autenticação/persistência para o ambiente de dev, com a justificativa de que o walking skeleton não precisa de segurança de produção. Concordei — adicionar auth agora seria complexidade sem ganho na avaliação.
- **Fase 2 — D3 (Smoke test programático)**: A IA propôs ir além do critério mínimo do roadmap (`docker compose ps` healthy) e adicionar smoke tests em pytest com conexão real. Concordei — demonstra que a infra não apenas "subiu" mas está funcionalmente acessível a partir do código Python.
- **Fase 2 — D4 (Makefile)**: Eu pedi para adicionar Makefile como entry point unificado. A IA incorporou com targets help/up/down/ps/logs/test-smoke/test/lint/clean, usando `-m smoke` (pytest marker) em vez de `-k smoke` (substring match) para maior precisão. Concordei com a abordagem.
- **Fase 3 — D1 (argparse stdlib)**: A IA propôs usar argparse em vez de typer/click para evitar dependências novas. Concordei — a CLI tem 6 flags e argparse é suficiente.
- **Fase 3 — D2 (maquinas.csv como roteamento)**: A IA propôs ler `maquinas.csv` apenas como tabela interna de roteamento (`maquina_id → galpão, linha`), sem publicá-lo como mensagem. Concordei — os dados de catálogo pertencem ao modelo de dados (Fase 4), não ao simulador.
- **Fase 3 — D3 (intervalo fixo + speed multiplier)**: A IA propôs `--interval` com `--speed` como multiplicador, evitando o modo "real-time por timestamps". Concordei — mais simples, previsível, e não depende de timestamps corretos nos fixtures.
- **Fase 3 — D4 (QoS 1 padrão)**: A IA propôs QoS 1 (at least once) para todas as mensagens, exercitando a idempotência que o consumidor (Fase 5) precisará tratar. Concordei — alinhado com o eixo de avaliação Event-Driven & MQTT.

### 3.3 O que eu revisei/corrigi no que a IA gerou

- **`[build-system]` prematuro**: A IA adicionou `[build-system]` com hatchling no TG1, mas o build quebrou porque `src/oee_textil/` ainda não existia. Corrigi: movi o `[build-system]` para o TG2, quando o pacote já existe.
- **`__main__.py` faltando**: `python -m oee_textil` falhou porque o pacote não tinha `__main__.py`. A IA não previu isso no plano inicial; adicionei o arquivo e corrigi o smoke test.
- **ruff format**: Vários arquivos gerados pela IA falharam `ruff format --check` (docstrings com trailing whitespace, falta de blank line após imports). O ruff fixou automaticamente; a lição é rodar o formatador antes de commitar, não depois.
- **Fase 1 — `Annotated[Union]` não é instanciável**: A IA usou `Annotated[Union[...], Field(discriminator="schema")]` como tipo diretamente instanciável via `MensagemMQTT(**data)`. Em Python 3.14 + Pydantic v2, `Annotated` não é callable — corrigi usando `TypeAdapter` com `validate_python()`.
- **Fase 1 — Campo `schema` shadowing BaseModel**: A IA usou `schema` como nome de campo, que conflita com `BaseModel.model_json_schema()`. Corrigi com `model_config = {"protected_namespaces": ()}` e `# type: ignore[assignment]`.
- **Fase 1 — E501 vs ruff format**: A descrição longa do campo `planejada` causou conflito entre E501 (linha longa) e ruff format (queria juntar a string). Corrigi encurtando a descrição.
- **Fase 2 — `test_smoke.py` já existia**: A IA tentou sobrescrever `tests/test_smoke.py` (criado na Fase 0 com testes de importabilidade). Corrigi: mantive os testes existentes e adicionei os novos testes de infra com `@pytest.mark.smoke` no mesmo arquivo, separados por comentários de seção.
- **Fase 2 — `-m smoke` vs `-k smoke`**: O plano original usava `-k smoke` no Makefile, mas isso capturaria os testes da Fase 0 por substring match no nome do arquivo. A IA ajustou para `-m smoke` (pytest marker), que seleciona apenas os testes explicitamente marcados — mais preciso.
- **Fase 2 — pre-commit corrigiu formatação**: O ruff format ajustou formatação do `test_smoke.py` no commit (quebra de linha em chamada de função longa). Nada grave — o pre-commit hook funcionou como esperado.
- **Fase 3 — `TypeAdapter` retorna `Any`**: O `MensagemMQTT.validate_python()` da Fase 1 retorna `Any`, então `msg.maquina_id` não tem tipo conhecido pelo mypy. A IA primeiro tentou `# type: ignore[attr-defined]` (que mypy marcou como unused), depois removeu o ignore completamente — mypy aceitou porque os atributos existem em todos os tipos da union. Funcionou, mas a anotação explícita com cast seria mais segura.
- **Fase 3 — `CallbackAPIVersion` não exportado**: O mypy reclamou que `paho.mqtt.client` não exporta explicitamente `CallbackAPIVersion`. A IA adicionou `# type: ignore[attr-defined]` no `cli.py` — correto, é uma limitação dos stubs do paho-mqtt.
- **Fase 3 — `test_entry_point_executa` da Fase 0 não quebrou**: A IA notou que o `__main__.py` do simulador (`python -m oee_textil.simulador`) é diferente do entry point principal (`python -m oee_textil`). O teste da Fase 0 continuou passando sem alterações — bom sinal de isolamento entre fases.

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
