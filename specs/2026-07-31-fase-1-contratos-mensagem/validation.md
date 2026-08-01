# Validation — Fase 1: Contratos de mensagem

> Procedimento executável de validação da Fase 1. Rode as verificações abaixo
> **na ordem** após executar todos os grupos de tarefas de [plan.md](plan.md).
> Referência de requisitos: [requirements.md](requirements.md).
> Critério de saída do [roadmap](../../specs/roadmap.md): `uv run pytest -k
> contract` verde.

---

## V1 — Modelos Pydantic (TG1)

- [ ] **1.1** `pydantic` aparece em `[project].dependencies` do `pyproject.toml`.
  ```bash
  grep -q pydantic pyproject.toml && echo "OK"
  ```
- [ ] **1.2** `src/oee_textil/schemas/mensagens.py` existe e contém 4 classes:
  `TelemetriaV1`, `EstadoV1`, `ParadaV1`, `ProducaoV1` + `MensagemMQTT`
  (discriminated union).
- [ ] **1.3** Testes unitários passam:
  ```bash
  uv run pytest -k schemas -v
  ```
- [ ] **1.4** `uv run mypy` strict passa sem erros.

---

## V2 — JSON Schema exportado (TG2)

- [ ] **2.1** `docs/contracts/README.md` existe.
- [ ] **2.2** Os 4 arquivos `.schema.json` existem e são JSON válido:
  ```bash
  ls docs/contracts/telemetria.v1.schema.json \
     docs/contracts/estado.v1.schema.json \
     docs/contracts/parada.v1.schema.json \
     docs/contracts/producao.v1.schema.json
  ```
- [ ] **2.3** Cada `.schema.json` contém `$schema`, `title`, `type`, `properties`.
- [ ] **2.4** Teste de JSON Schema passa:
  ```bash
  uv run pytest -k json_schema -v
  ```

---

## V3 — Contract tests dos fixtures (TG3)

- [ ] **3.1** `tests/test_contracts.py` existe com 3 funções de teste.
- [ ] **3.2** `test_telemetria_ndjson`: valida ≥ 4 linhas de `telemetria.ndjson`.
- [ ] **3.3** `test_estado_parada_ndjson`: valida ≥ 5 linhas de
  `estado-parada.ndjson` (inclui a duplicata — ambas as linhas idênticas
  passam).
- [ ] **3.4** `test_producao_ndjson`: valida ≥ 3 linhas de `producao.ndjson`.
- [ ] **3.5** `uv run pytest -k contract -v` passa (todos os contract tests
  verdes).
- [ ] **3.6** Nenhuma linha dos fixtures foi alterada (verificar com `git
  diff data/` — deve estar vazio).

---

## V4 — ADR-002 (TG4)

- [ ] **4.1** `docs/adr/002-versionamento-schema-evolucao-aditiva.md` existe.
- [ ] **4.2** Segue o template: Status **Aceito**, Data **2026-07-31**,
  Decisores **Samuel Oliveira**.
- [ ] **4.3** Seção _Contexto_ menciona contratos versionados como fronteira e
  o eixo Event-Driven & MQTT.
- [ ] **4.4** Seção _Decisão_ descreve evolução aditiva e campo `schema` como
  discriminador.
- [ ] **4.5** Tabela de _Alternativas_ tem ≥ 3 entradas (ex.: protobuf/Avro,
  schema registry, sem versionamento).
- [ ] **4.6** Seção _Consequências_ preenchida (positivas, negativas, gatilho
  de reavaliação).

---

## V5 — Barra completa e registros (TG5)

- [ ] **5.1** `uv run ruff check` verde.
- [ ] **5.2** `uv run ruff format --check` verde.
- [ ] **5.3** `uv run mypy` verde (strict, zero erros).
- [ ] **5.4** `uv run pytest` verde (todos os testes: unitários + contract +
  smoke da Fase 0).
- [ ] **5.5** `docs/AI_ASSISTED.md` tem entrada da Fase 1 preenchida.

### Comando único da barra

```bash
uv run ruff check && \
  uv run ruff format --check && \
  uv run mypy && \
  uv run pytest -v && \
  echo "FASE 1: TODOS OS GATES VERDES"
```

---

## Resumo

| Verificação | Descrição | Resultado |
|-------------|-----------|-----------|
| V1 | Modelos Pydantic (4 schemas + union) | ✅ / ❌ |
| V2 | JSON Schema exportado (4 arquivos) | ✅ / ❌ |
| V3 | Contract tests (fixtures NDJSON) | ✅ / ❌ |
| V4 | ADR-002 (versionamento de schema) | ✅ / ❌ |
| V5 | Barra completa e registros | ✅ / ❌ |

> **Fase 1 fechada quando:** todas as verificações V1–V5 = ✅.
> **Fase 0 deve continuar verde** (smoke test da Fase 0 não pode quebrar).
