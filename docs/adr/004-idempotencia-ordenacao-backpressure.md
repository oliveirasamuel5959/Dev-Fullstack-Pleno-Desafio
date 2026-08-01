# ADR-004: Idempotência, ordenação e backpressure na ingestão MQTT

- **Status:** Aceito
- **Data:** 2026-08-01
- **Decisores:** Samuel Oliveira

## Contexto

A Fase 5 implementa o consumidor MQTT — a primeira fatia ponta a ponta do
walking skeleton (simulador → broker → consumidor → banco). O sistema recebe
mensagens com QoS 1 (at least once) de ~200 máquinas publicando a cada 1–5 s.
As mensagens podem duplicar (reenvio por timeout de ACK), chegar fora de ordem
(`ts_sensor` não monotônico), e conter defeitos (fixtures com duplicata e
out-of-order intencionais).

Restrições:
- OEE depende de dados corretos e não duplicados
- Eventos (`estado_maquina`, `parada`, `producao`) não têm PK natural —
  múltiplos tipos de evento por máquina×timestamp
- O banco é PostgreSQL + TimescaleDB com modelo raw-first (ADR-003)
- A missão (§4.4) exige tratar: late events, clock drift, duplicatas,
  idempotência, backpressure e dead-letter

## Decisão

### 1. Idempotência por chave natural (telemetria)

`Telemetria` tem PK composta `(maquina_id, ts_sensor)` — a chave natural de
dedup. `INSERT ... ON CONFLICT (maquina_id, ts_sensor) DO NOTHING` garante
que duplicatas são silenciosamente ignoradas. Um sensor publica no máximo
1 leitura por tick — se houver reenvio, a PK barra.

### 2. Idempotência por content hash (eventos)

`EstadoMaquina`, `Parada` e `Producao` não têm PK natural. A estratégia:
coluna `content_hash VARCHAR(64)` com `UNIQUE` constraint. O hash é SHA-256
dos campos relevantes da mensagem (excluindo `ts_ingestao`, `id` e o próprio
`content_hash`), calculado no Python antes do INSERT.

`INSERT ... ON CONFLICT (content_hash) DO NOTHING` — a duplicata intencional
do fixture `estado-parada.ndjson` (linhas 6 e 7 idênticas) resulta em
exatamente 1 row inserida.

Risco de colisão SHA-256 é desprezível para o volume do skeleton. Em produção,
considerar hash composto com schema+maquina_id+ts_sensor.

### 3. Ordenação por buffer com janela de reordenação

Mensagens podem chegar com `ts_sensor` fora de ordem. O consumidor mantém
um buffer em memória por `maquina_id`. Mensagens dentro da janela de
reordenação (default 30s) são reordenadas por `ts_sensor` antes do INSERT.
Mensagens fora da janela (>30s de atraso) são inseridas imediatamente com
log de "late event".

O buffer é drenado no graceful shutdown (SIGINT/SIGTERM → fecha subscriber →
processa buffer restante → fecha sessão DB).

### 4. Backpressure via QoS 1 + ACK após persistência

O broker entrega mensagens com QoS 1 (at least once). O consumidor confirma
o recebimento (ACK) somente após a persistência bem-sucedida no banco. Se
o banco estiver lento, o broker reenvia a mensagem (duplicata), e o dedup
(§1, §2) garante que não há duplicação lógica.

aiomqtt gerencia o ACK automaticamente — o `async for message in
client.messages` só avança após o callback retornar (ou lançar exceção).

### 5. Dead-letter como arquivo NDJSON

Mensagens que falham validação Pydantic (schema desconhecido, campos
ausentes, JSON inválido) são appendadas em `data/dead-letter.ndjson` com
`{payload, erro, topico, ts_ingestao}`. Simples, inspecionável, sem
migração extra. O arquivo é montado como volume no container para persistir
fora do ciclo de vida do container.

## Alternativas consideradas

| Alternativa | Por que não |
|-------------|-------------|
| Dead-letter como tópico MQTT | Adiciona complexidade (pub/sub extra) sem ganho real para o skeleton; arquivo é mais simples de inspecionar |
| Dedup por hash no broker (Mosquitto plugin) | Mosquitto não tem plugin de dedup nativo; dependeria de infra externa |
| Ordenação no banco (ORDER BY ts_sensor) | Ordenar na query não resolve duplicatas; o INSERT ainda inseriria fora de ordem |
| PK surrogate + unique constraint separada em telemetria | TimescaleDB exige que toda unique constraint inclua a coluna de particionamento; surrogate exigiria índice extra |
| Backpressure por fila externa (Redis/Kafka) | Overkill para o walking skeleton; QoS 1 + dedup no banco é suficiente |

## Consequências

**Positivas:**
- Dedup no nível do banco (constraints) — garantia forte, não depende de
  estado em memória
- Content hash é determinístico e imune a clock drift
- Dead-letter como NDJSON é trivial de inspecionar e rotacionar
- Buffer de ordenação em memória é leve (~200 máquinas × poucas mensagens)

**Negativas:**
- Content hash não detecta duplicatas com `ts_sensor` diferente (ex.: mesma
  parada reportada 2× com timestamps diferentes) — edge case aceito para o
  skeleton
- Buffer de ordenação em memória perde mensagens não drenadas em crash
  (não há WAL para o buffer)
- ON CONFLICT com `index_elements` requer nome explícito — sensível a
  renomeação de colunas

**Gatilho de reavaliação:**
- Volume de duplicatas alto (>10%) → reavaliar dedup no broker ou fila
- Perda de mensagens por crash do consumidor → WAL ou buffer em disco
- Necessidade de dead-letter queryable → migrar para tabela no banco
