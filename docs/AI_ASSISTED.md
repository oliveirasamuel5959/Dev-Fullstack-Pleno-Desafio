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
| _ex.: Copilot_ | _scaffolding do consumidor MQTT_ | _..._ |

### 3.2 Decisões em que a IA ajudou - e onde eu discordei dela
- _ex.: A IA sugeriu QoS 2 em tudo; optei por QoS 1 + idempotência porque..._

### 3.3 O que eu revisei/corrigi no que a IA gerou
- _ex.: Corrigi o cálculo de Performance que a IA deixou sem clamp em [0,1]._

### 3.4 Como otimizei o repositório para IA
- _ex.: Criei AGENTS.md com comandos de build/test e mapa de bounded contexts._

### 3.5 Prompts relevantes (opcional, mas valorizado)
- _Cole 1–3 prompts que foram decisivos, com o racional._

---

## 4. Como isso é avaliado (objetivo)

| Sub-critério | Atende quando... |
|--------------|------------------|
| Harness executável presente | Há teste/linter/contract-test que roda e falha se algo quebra |
| Uso de IA documentado | `AI_ASSISTED.md` preenchido com decisões e revisões reais |
| Otimização de contexto | Existe ≥1 artefato (AGENTS.md/instructions/prompts) útil e coerente |
| Pensamento crítico sobre IA | Há ao menos um caso em que o candidato **discordou/corrigiu** a IA |
