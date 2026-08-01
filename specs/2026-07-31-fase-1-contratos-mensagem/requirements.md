# Requirements — Fase 1: Contratos de mensagem

> Feature derivada de [`../../specs/roadmap.md`](../../specs/roadmap.md) — Fase 1.
> Conformidade obrigatória com [`../../specs/mission.md`](../../specs/mission.md)
> e [`../../specs/tech-stack.md`](../../specs/tech-stack.md).
> Branch de trabalho: `desafio/samuel-oliveira`.

## 1. Contexto

O roadmap manda: **os 4 schemas como código, não como prosa**. Hoje o repositório
tem o harness da Fase 0 (pytest + ruff + mypy + pre-commit + layout `src/`), mas
nenhum código de domínio. Esta feature transforma os contratos de mensagem
descritos em `docs/ESPECIFICACAO_TECNICA.md` §2 em modelos Pydantic v2
validáveis, exporta JSON Schema para `docs/contracts/`, e implementa o primeiro
_contract test_ — um teste que valida **cada linha JSON** dos fixtures
`data/exemplos-mqtt/*.ndjson` contra o modelo correspondente.

O eixo "Event-Driven & MQTT" da avaliação depende de schemas versionados:
contratos de mensagem são a **fronteira mais externa** do sistema — tudo que
entra (consumidor MQTT) ou sai (simulador) passa por eles. Erros de schema
detectados aqui não chegam ao domínio.

## 2. Escopo

### Dentro

- Adicionar `pydantic>=2` como dependência (via `uv add`).
- Criar 4 modelos Pydantic v2 em `src/oee_textil/schemas/`:
  - `TelemetriaV1` (campos: `schema`, `maquina_id`, `ts_sensor`, `rpm`,
    `voltas_acumuladas`, `temperatura_c`, `vibracao_mm_s`)
  - `EstadoV1` (campos: `schema`, `maquina_id`, `ts_sensor`, `estado`,
    `estado_anterior`)
  - `ParadaV1` (campos: `schema`, `maquina_id`, `ts_sensor`, `motivo_codigo`,
    `motivo_descricao`, `planejada`)
  - `ProducaoV1` (campos: `schema`, `maquina_id`, `ts_sensor`,
    `unidades_produzidas`, `unidades_refugo`, `ordem_producao`)
- Validações: `schema` como `Literal` do valor exato (`"telemetria.v1"`, etc.);
  `ts_sensor` como `datetime` UTC; `rpm >= 0`; `unidades_produzidas >= 0`;
  `unidades_refugo >= 0`; `estado` como `Literal` dos estados válidos.
- _Discriminated union_ no nível de schema: um `type` union que despacha pelo
  campo `schema` para o modelo correto — base do contract test.
- Exportar JSON Schema de cada modelo para `docs/contracts/` (4 arquivos
  `.schema.json`).
- Contract test em `tests/test_contracts.py`: lê cada `.ndjson`, extrai linhas
  JSON (ignora `//` comentários e linhas vazias), despacha pelo campo `schema`
  para o modelo Pydantic, valida — **toda linha deve passar**. Os defeitos
  intencionais (duplicata, fora de ordem, `rpm=0`) são válidos no nível de
  schema; o tratamento deles é responsabilidade do consumidor (Fase 5).
- **ADR-002**: versionamento de schema (evolução aditiva, campo `schema` como
  discriminador), a partir de `docs/adr/000-template.md`.

### Fora (explicitamente)

- Consumidor MQTT, broker, banco de dados (Fases 2–5).
- Tratamento de duplicatas/ordenação/idempotência (Fase 5).
- Cálculo de OEE (Fase 6).
- Qualquer endpoint HTTP ou dashboard (Fases 7–8).

## 3. Decisões travadas

### D1 — Pydantic v2 com `Literal` para o campo `schema`

Cada modelo tem `schema: Literal["<nome>.v1"]` como campo obrigatório. O valor
exato do literal é fixo por versão de schema; qualquer `schema` desconhecido ou
ausente falha a validação. Isto implementa a regra de missão §4.5 ("contratos
versionados, evolução que não quebra consumidores").

### D2 — Discriminated union para despacho

Uma `Annotated[Union[...], Field(discriminator="schema")]` permite que o
contract test leia uma linha JSON, inspecione o campo `schema`, e instancie o
modelo correto **sem if/elif manual**. A mesma union será usada pelo consumidor
na Fase 5.

### D3 — Contract test valida TODAS as linhas

Cada linha JSON dos 3 arquivos NDJSON (`telemetria.ndjson`,
`estado-parada.ndjson`, `producao.ndjson`) deve ser parseável por **algum**
modelo da union. Linhas que começam com `//` são comentários e ignoradas; linhas
vazias também. O teste conta linhas processadas e falha se zero.

Os defeitos intencionais (`rpm=0`, duplicata, fora de ordem) são **válidos no
nível de schema** — eles representam cenários reais de fábrica (máquina parada,
reenvio de mensagem, late arrival). Rejeitá-los no schema seria um erro de
design. O tratamento (dedup, ordenação) pertence ao consumidor (Fase 5).

### D4 — JSON Schema exportado como artefato versionado

`docs/contracts/` contém 4 arquivos `.schema.json` gerados por
`model_json_schema()`. Eles são commitados e servem como contrato externo para
consumidores que não usam Python (ex.: um simulador em outra linguagem, ou
documentação para a banca).

### D5 — ADR-002: evolução aditiva

A estratégia de versionamento é **evolução aditiva**:
- Campos novos são adicionados como **opcionais com default** (ex.: `Optional`
  com `default=None`).
- Nenhum campo existente é removido ou renomeado.
- O campo `schema` é o discriminador de versão — `telemetria.v2` seria um novo
  modelo com seu próprio `Literal["telemetria.v2"]`.
- Payload sem campo `schema` ou com schema desconhecido → rejeitado na borda
  (dead-letter na Fase 5).

## 4. Restrições

- Nenhuma regra de [mission.md](../../specs/mission.md) §4 pode ser violada
  (§4.5 — contratos versionados — é o foco desta fase).
- Stack conforme [tech-stack.md](../../specs/tech-stack.md): apenas Pydantic v2
  entra como nova dependência.
- Documentação em pt-BR; identificadores de campo em português (`maquina_id`,
  `motivo_codigo`, `ts_sensor`, etc.) mantidos como estão nos fixtures.
- Os arquivos em `data/exemplos-mqtt/` **não podem ser alterados** (missão §4.7).

## 5. Riscos e observações

- **Comentários nos NDJSON**: os arquivos têm linhas `//` que não são JSON
  válido. O parser do contract test precisa filtrá-las. Isso não é um risco —
  é parte do design.
- **`estado-parada.ndjson` mistura dois schemas**: é o único arquivo que
  contém mensagens de tipos diferentes (`estado.v1` e `parada.v1`). O
  discriminated union resolve isso naturalmente.
- **`rpm=0` não é um erro de schema**: RPM zero é um valor válido (máquina
  parada). O que o domínio faz com esse valor (calcular Disponibilidade) é
  responsabilidade da Fase 6, não daqui.
- **pydantic** pode puxar `pydantic-core` compilado — verificar se `uv add`
  funciona sem conflito com o ambiente.
