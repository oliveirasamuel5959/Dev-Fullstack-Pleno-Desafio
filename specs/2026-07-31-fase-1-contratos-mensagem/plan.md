# Plan — Fase 1: Contratos de mensagem

> Execução de [requirements.md](requirements.md). Grupos de tarefas numerados,
> executados **em ordem**; cada grupo termina em verificação + commit próprio.
> Critério de aceite final em [validation.md](validation.md).

## TG1 — Dependência e scaffold dos schemas

- **1.1** `uv add pydantic` (v2, já que Python ≥3.14).
- **1.2** Criar `src/oee_textil/schemas/mensagens.py` com os 4 modelos
  Pydantic usando `BaseModel`, `Literal` para `schema`, `datetime` para
  `ts_sensor`, `conint(ge=0)` para contadores, `float` com `ge=0` para rpm.
- **1.3** Criar a discriminated union `MensagemMQTT` com
  `Annotated[Union[...], Field(discriminator="schema")]` contendo os 4 modelos.
- **1.4** Teste unitário `tests/test_schemas.py`: instancia cada modelo com
  dados válidos dos fixtures; verifica que `schema` errado, campo ausente e
  tipo inválido levantam `ValidationError`.
- **Verificação:** `uv run pytest -k schemas` verde; `uv run mypy` strict verde.
- **Commit:** `feat: modelos Pydantic dos 4 schemas MQTT (v1)`

## TG2 — Export de JSON Schema

- **2.1** Criar `docs/contracts/` com um `README.md` explicando o propósito
  (contrato versionado, gerado por Pydantic, fonte da verdade).
- **2.2** Script ou função `export_schemas()` que chama `model_json_schema()`
  em cada modelo e escreve `docs/contracts/telemetria.v1.schema.json`,
  `estado.v1.schema.json`, `parada.v1.schema.json`, `producao.v1.schema.json`.
- **2.3** Teste que verifica que os 4 arquivos existem, são JSON válido e
  contêm `$schema` e `properties`.
- **Verificação:** `uv run pytest -k json_schema` verde; arquivos commitados.
- **Commit:** `feat: export JSON Schema para docs/contracts/`

## TG3 — Contract test dos fixtures NDJSON

- **3.1** Criar `tests/test_contracts.py`:
  - `load_ndjson(path)`: lê arquivo linha a linha, ignora `//` e linhas vazias,
    faz `json.loads` em cada linha restante.
  - `test_telemetria_ndjson`: carrega `telemetria.ndjson`, valida cada linha
    contra `TelemetriaV1`, conta linhas ≥ 4.
  - `test_estado_parada_ndjson`: carrega `estado-parada.ndjson`, despacha cada
    linha via `MensagemMQTT` (discriminated union), conta total ≥ 5,
    conta duplicata de parada presente (linhas 6 e 7 idênticas).
  - `test_producao_ndjson`: carrega `producao.ndjson`, valida contra
    `ProducaoV1`, conta ≥ 3.
- **3.2** Garantir que **todas** as linhas JSON dos 3 arquivos passam na
  validação — nenhuma linha válida é rejeitada.
- **Verificação:** `uv run pytest -k contract` verde (roda só os contract
  tests); `uv run pytest` verde (todos).
- **Commit:** `test: contract tests validando fixtures NDJSON contra schemas`

## TG4 — ADR-002: versionamento de schema

- **4.1** Criar `docs/adr/002-versionamento-schema-evolucao-aditiva.md` a
  partir de `docs/adr/000-template.md`: Status **Aceito**, Data **2026-07-31**,
  Decisores **Samuel Oliveira**.
- **4.2** Conteúdo: contexto (eixo Event-Driven & MQTT, contratos versionados
  como fronteira); decisão (D5 — evolução aditiva, campo `schema` como
  discriminador, rejeição de schemas desconhecidos); alternativas (protobuf,
  schema registry externo, sem versionamento); consequências.
- **Verificação:** ADR segue o template; seções completas.
- **Commit:** `docs: ADR-002 versionamento de schema com evolução aditiva`

## TG5 — Gates finais e registros

- **5.1** Rodar a barra completa: `uv run ruff check`, `uv run ruff format
  --check`, `uv run mypy`, `uv run pytest`.
- **5.2** Atualizar `docs/AI_ASSISTED.md`: entrada da Fase 1.
- **5.3** Executar o procedimento de [validation.md](validation.md).
- **Commit:** `docs: registro AI_ASSISTED (Fase 1)` → push.
