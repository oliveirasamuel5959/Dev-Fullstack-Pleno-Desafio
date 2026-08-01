# Requirements — Fase 5: Consumidor de ingestão

> Feature derivada de [`../../specs/roadmap.md`](../../specs/roadmap.md) — Fase 5.
> Conformidade obrigatória com [`../../specs/mission.md`](../../specs/mission.md)
> e [`../../specs/tech-stack.md`](../../specs/tech-stack.md).
> Branch de trabalho: `desafio/samuel-oliveira`.

## 1. Contexto

O roadmap manda: **primeira fatia ponta a ponta, resistente aos defeitos
intencionais**. Hoje o repositório tem: schemas Pydantic (Fase 1), broker
Mosquitto + TimescaleDB (Fase 2), simulador publicando mensagens (Fase 3),
e modelo de dados com 7 tabelas (Fase 4). O que falta é o elo que fecha o
ciclo: um consumidor MQTT que assina `fabrica/#`, valida, desduplica e
persiste as mensagens no banco.

Esta feature implementa o consumidor assíncrono com aiomqtt, a estratégia
de dedup (PK natural para telemetria, content hash para eventos), dead-letter
em arquivo NDJSON, e a containerização do serviço (Dockerfile + compose).

**Gate de saída:** simulador → broker → consumidor → banco funcionando; teste
de dedup verde.

## 2. Escopo

### Dentro

- **Dependência `aiomqtt`**: `uv add aiomqtt` — cliente MQTT assíncrono sobre
  asyncio, encaixa no event loop sem threads extras (tech-stack §Mensageria).
- **Config MQTT** em `core/config.py`: `get_mqtt_broker_host()`,
  `get_mqtt_broker_port()` com env vars `MQTT_BROKER_HOST`/`MQTT_BROKER_PORT`
  e fallback `localhost:1883`.
- **`.env`/`.env.example`**: adicionar `MQTT_BROKER_HOST` e `MQTT_BROKER_PORT`.
- **Nova migração Alembic**: adicionar coluna `content_hash VARCHAR(64)` +
  `UNIQUE` constraint em `estado_maquina`, `parada`, `producao`. A constraint
  garante idempotência no nível do banco — duplicatas são rejeitadas com
  `ON CONFLICT (content_hash) DO NOTHING`.
- **Consumidor** (`src/oee_textil/services/consumidor.py`):
  - `async def main()` — entry point executável via
    `python -m oee_textil.services.consumidor`
  - Subscribe `fabrica/#` com QoS 1
  - Pipeline por mensagem: validar (Pydantic) → calcular hash → inserir
  - **Validação**: `MensagemMQTT.validate_python(payload)` — falhas vão para
    dead-letter
  - **Dedup**: `ON CONFLICT DO NOTHING` — telemetria usa PK natural
    `(maquina_id, ts_sensor)`, eventos usam `content_hash` UNIQUE
  - **Dead-letter**: append em `data/dead-letter.ndjson` com
    `{payload, erro, ts_ingestao, topico}`
  - **Ordenação**: buffer por `maquina_id` com janela de reordenação
    configurável (default 30s) — eventos fora de ordem dentro da janela são
    reordenados por `ts_sensor`
  - **Graceful shutdown**: SIGINT/SIGTERM → fecha subscriber → drena buffer →
    fecha sessão DB
- **Dockerfile**: multi-estágio Python 3.14 + uv sync. Entry point padrão
  `python -m oee_textil.services.consumidor`. Imagem única reutilizável para
  API (Fase 7) e simulador.
- **docker-compose.yml**: adicionar serviço `consumidor` (build, rede
  `oee-network`, depends_on mosquitto + timescaledb com healthchecks).
- **Testes**:
  - Unitários: hash, validação, roteamento schema→tabela
  - Integração: consumidor real com broker + banco, verifica dedup com
    fixtures (duplicata, fora de ordem, `rpm=0`)
- **ADR-004**: idempotência (PK natural + content hash), ordenação (buffer
  com janela), backpressure (QoS 1 + ACK após persistência).

### Fora (explicitamente)

- Cálculo de OEE (Fase 6)
- API HTTP / dashboard (Fases 7–8)
- Autenticação/TLS no MQTT
- Dead-letter como tópico MQTT separado (é arquivo NDJSON)

## 3. Decisões travadas

### D1 — aiomqtt (async) para o consumidor

O consumidor é um subscriber MQTT de longa duração — o modelo async evita
threads bloqueadas e compartilha o event loop com o banco (via
`run_in_executor` para SQLAlchemy sync ou `aiosqlite`-like). O simulador
continua com paho-mqtt síncrono (CLI de curta duração).

### D2 — Content hash para dedup de eventos

Eventos (`estado_maquina`, `parada`, `producao`) não têm PK natural
( múltiplos tipos por máquina×timestamp). A estratégia: SHA-256 dos campos
relevantes da mensagem (excluindo `ts_ingestao`), armazenado em coluna
`content_hash VARCHAR(64)` com `UNIQUE` constraint.

`ON CONFLICT (content_hash) DO NOTHING` — duplicatas são silenciosamente
ignoradas. A duplicata intencional do fixture `estado-parada.ndjson`
(linhas 6 e 7 idênticas) resulta em exatamente 1 row inserida.

### D3 — PK natural para telemetria (sem content hash)

`telemetria` já tem PK composta `(maquina_id, ts_sensor)` que é a chave
natural de dedup (um sensor publica ≤1 leitura por tick). `ON CONFLICT
(maquina_id, ts_sensor) DO NOTHING` é suficiente — não precisa de hash.

### D4 — Dead-letter como arquivo NDJSON

Mensagens que falham validação Pydantic são appendadas em
`data/dead-letter.ndjson` (uma linha JSON por falha, mesmo formato dos
fixtures). Simples, inspecionável com `cat`, sem migração extra.

O arquivo é montado via volume no container para persistir fora do ciclo
de vida do container.

### D5 — Ordenação via buffer com janela

Mensagens podem chegar fora de ordem (`ts_sensor` anterior ao último
processado). O consumidor mantém um buffer por `maquina_id` com janela
de reordenação configurável (default 30s). Mensagens dentro da janela são
reordenadas; mensagens fora da janela (>30s de atraso) são inseridas
imediatamente com log de "late event".

### D6 — SQLAlchemy sync com run_in_executor

aiomqtt é assíncrono, mas SQLAlchemy 2.0 com psycopg2 é síncrono. Em vez
de adicionar `asyncpg` + `sqlalchemy[asyncio]` (dependência nova, migração
de engine), usamos `loop.run_in_executor(None, sync_insert, ...)` para não
bloquear o event loop. Suficiente para o walking skeleton.

### D7 — Dockerfile multi-entrada

Uma única imagem Python com `uv sync`. O entry point padrão é o consumidor;
para API (Fase 7), basta `docker compose run --rm api` com `command`
override. Segue ADR-001: "um container, comandos diferentes".

### D8 — ADR-004 (não ADR-003)

ADR-003 foi consumido pela Fase 4 (modelagem de dados). O roadmap previa
ADR-003 para idempotência, mas a ordem cronológica real prevalece. ADR-004
cobre idempotência, ordenação e backpressure.

## 4. Restrições

- Nenhuma regra de [mission.md](../../specs/mission.md) §4 pode ser violada.
- Stack conforme [tech-stack.md](../../specs/tech-stack.md): aiomqtt entra
  como dependência nova.
- Os defeitos intencionais em `data/exemplos-mqtt/` devem ser **tratados**,
  não "limpados" (mission §4.7).
- SQLAlchemy sync + psycopg2 (não migrar para asyncpg nesta fase).
- Testes das Fases 0–4 devem continuar verdes (sem regressão).

## 5. Riscos e observações

- **aiomqtt vs paho-mqtt**: ambos coexistem no mesmo projeto sem conflito
  (Fase 3 usa paho-mqtt, Fase 5 usa aiomqtt). São pacotes diferentes.
- **Content hash vs colisão**: SHA-256 tem probabilidade de colisão
  desprezível para o volume do skeleton. Em produção, considerar hash
  composto (schema+maquina_id+ts_sensor+payload).
- **Buffer de ordenação**: manter buffers por máquina em memória. Com ~200
  máquinas, o footprint é pequeno. O buffer é drenado no shutdown.
- **Docker build**: primeira build pode ser lenta (uv sync + compilação).
  Usar cache de camadas (pyproject.toml/uv.lock primeiro, depois src/).
- **Dead-letter no container**: o arquivo precisa ser montado como volume
  para persistir fora do ciclo de vida do container. Sem volume, os dados
  somem no `docker compose down`.
