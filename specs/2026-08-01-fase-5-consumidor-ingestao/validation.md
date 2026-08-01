# Validation — Fase 5: Consumidor de ingestão

> Procedimento executável de validação da Fase 5. Rode as verificações abaixo
> **na ordem** após executar todos os grupos de tarefas de [plan.md](plan.md).
> Critério de saída do [roadmap](../../specs/roadmap.md): simulador → broker →
> consumidor → banco funcionando; teste de dedup verde.

---

## V1 — aiomqtt + config MQTT (TG1)

- [ ] **1.1** `aiomqtt` aparece em `pyproject.toml` dependencies.
- [ ] **1.2** `core/config.py` tem `get_mqtt_broker_host()` e
  `get_mqtt_broker_port()`.
- [ ] **1.3** `.env` e `.env.example` incluem `MQTT_BROKER_HOST` e
  `MQTT_BROKER_PORT`.
- [ ] **1.4** Testes de config passam (incluindo os novos):
  ```bash
  uv run pytest -k config -v
  ```

---

## V2 — Migração content_hash (TG2)

- [ ] **2.1** Nova migração existe em `migrations/versions/`.
- [ ] **2.2** Colunas `content_hash VARCHAR(64)` nas 3 tabelas de evento:
  ```bash
  docker exec oee-timescaledb psql -U oee -d oee_textil -c "\d estado_maquina" | grep content_hash
  docker exec oee-timescaledb psql -U oee -d oee_textil -c "\d parada" | grep content_hash
  docker exec oee-timescaledb psql -U oee -d oee_textil -c "\d producao" | grep content_hash
  ```
- [ ] **2.3** UNIQUE constraints existem em `content_hash`.
- [ ] **2.4** Migração aplica limpo (`make migrate` sem erro).
- [ ] **2.5** Round-trip downgrade/upgrade funciona.
- [ ] **2.6** Testes passam:
  ```bash
  uv run pytest -k migrations -v
  ```

---

## V3 — Consumidor (TG3)

- [ ] **3.1** `src/oee_textil/services/consumidor.py` existe com `main()`.
- [ ] **3.2** `python -m oee_textil.services.consumidor` é executável.
- [ ] **3.3** `calcular_content_hash` é determinístico (mesmo input → mesmo hash).
- [ ] **3.4** `calcular_content_hash` ignora `ts_ingestao`.
- [ ] **3.5** `resolver_tabela` mapeia 4 schemas → 4 modelos.
- [ ] **3.6** Dead-letter escreve NDJSON válido.
- [ ] **3.7** `inserir_telemetria` faz ON CONFLICT na PK natural.
- [ ] **3.8** `inserir_evento` faz ON CONFLICT no content_hash.
- [ ] **3.9** Teste ponta a ponta: simulador → consumidor → banco.
- [ ] **3.10** Teste de dedup: duplicata do fixture gera exatamente 1 row.
- [ ] **3.11** Testes passam:
  ```bash
  uv run pytest -k consumidor -v
  ```

---

## V4 — Dockerfile + compose (TG4)

- [ ] **4.1** `Dockerfile` existe na raiz.
- [ ] **4.2** `docker compose build consumidor` sem erro.
- [ ] **4.3** `docker compose up -d` mostra consumidor running.
- [ ] **4.4** `docker compose ps` mostra 3 serviços healthy.
- [ ] **4.5** Consumidor conecta ao Mosquitto (`docker compose logs consumidor`).
- [ ] **4.6** `make build` funciona (se adicionado ao Makefile).

---

## V5 — Gates de qualidade (TG5)

- [ ] **5.1** `make lint` verde.
- [ ] **5.2** `make test` verde (todos os testes).
- [ ] **5.3** `make test-smoke` verde.
- [ ] **5.4** Fases 0–4 sem regressão:
  ```bash
  uv run pytest -k "not consumidor" -v
  ```

---

## V6 — Registros (TG5)

- [ ] **6.1** `docs/adr/004-idempotencia-ordenacao-backpressure.md` existe.
- [ ] **6.2** `docs/AI_ASSISTED.md` tem entrada da Fase 5.
- [ ] **6.3** `specs/roadmap.md` atualizado com numeração real de ADRs.

---

## Fluxo completo de validação

```bash
# 1. Começar limpo
make clean

# 2. Subir infra + preparar banco
make up
make setup-db

# 3. Build do consumidor
docker compose build consumidor

# 4. Subir consumidor
docker compose up -d
docker compose ps  # 3 serviços healthy

# 5. Rodar simulador
uv run python -m oee_textil.simulador --interval 0.1

# 6. Verificar logs do consumidor
docker compose logs consumidor | tail -20

# 7. Verificar dados no banco
docker exec oee-timescaledb psql -U oee -d oee_textil -c "SELECT count(*) FROM telemetria;"
docker exec oee-timescaledb psql -U oee -d oee_textil -c "SELECT count(*) FROM estado_maquina;"
docker exec oee-timescaledb psql -U oee -d oee_textil -c "SELECT count(*) FROM parada;"
docker exec oee-timescaledb psql -U oee -d oee_textil -c "SELECT count(*) FROM producao;"

# 8. Rodar simulador de novo (testar dedup — counts não devem dobrar)
uv run python -m oee_textil.simulador --interval 0.1
docker exec oee-timescaledb psql -U oee -d oee_textil -c "SELECT count(*) FROM telemetria;"

# 9. Barra completa
make lint && make test

echo "FASE 5: TODOS OS GATES VERDES"
```

---

## Resumo

| Verificação | Descrição | Resultado |
|-------------|-----------|-----------|
| V1 | aiomqtt + config MQTT (env vars) | ✅ / ❌ |
| V2 | Migração content_hash UNIQUE (3 tabelas) | ✅ / ❌ |
| V3 | Consumidor (validate, hash, insert, dead-letter, dedup) | ✅ / ❌ |
| V4 | Dockerfile + compose service | ✅ / ❌ |
| V5 | Gates de qualidade (ruff, mypy, pytest sem regressão) | ✅ / ❌ |
| V6 | Registros (ADR-004, AI_ASSISTED.md) | ✅ / ❌ |

> **Fase 5 fechada quando:** todas as verificações V1–V6 = ✅ **e** fluxo ponta
> a ponta (simulador → broker → consumidor → banco) funcionando com dedup
> comprovado.
> **Fases 0–4 devem continuar verdes.**
