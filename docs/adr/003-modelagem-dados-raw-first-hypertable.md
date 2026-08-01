# ADR-003: Modelagem de dados — raw-first com hypertable TimescaleDB

- **Status:** Aceito
- **Data:** 2026-08-01
- **Decisores:** Samuel Oliveira

## Contexto

A Fase 4 exige persistência coerente com o modelo conceitual da
`docs/ESPECIFICACAO_TECNICA.md` §3: entidades de catálogo (máquinas,
motivos, turnos), eventos brutos (telemetria, estado, parada, produção)
e futuras agregações de OEE.

O banco é PostgreSQL 16 + TimescaleDB (imagem `timescale/timescaledb`,
Fase 2), escolhido para resolver tanto o eixo relacional quanto o
time-series com um único motor (ADR-001: monorepo, um pacote, redução
de complexidade operacional).

Restrições:
- ~200 máquinas publicando a cada 1–5 s → alta cardinalidade temporal
- Mensagens podem atrasar, duplicar, chegar fora de ordem
- OEE = Disponibilidade × Performance × Qualidade (produto, não média)
- `ts_sensor` (relógio do sensor) vs `ts_ingestao` (relógio do servidor)
  — deriva de relógio precisa ser rastreável

## Decisão

### 1. Eventos brutos como fonte da verdade (raw-first)

Todas as mensagens MQTT são persistidas **sem transformação** em tabelas
de evento (`telemetria`, `estado_maquina`, `parada`, `producao`). O dado
bruto é imutável e rastreável — qualquer agregação (OEE, Pareto) é
derivada, não substituta.

### 2. Hypertable TimescaleDB para telemetria

`telemetria` é particionada por `ts_sensor` via `create_hypertable(by_range)`.
A PK é composta `(maquina_id, ts_sensor)` — a chave natural de dedup
(um sensor publica no máximo 1 leitura por tick). O índice da PK cobre
consultas por máquina×janela sem índice extra.

### 3. Surrogate id nos eventos de estado/parada/produção

Eventos podem ter múltiplas mensagens válidas por máquina×timestamp
(tipos diferentes: `estado.v1` e `parada.v1` no mesmo instante). Sem PK
natural viável — usa `id BIGINT GENERATED ALWAYS AS IDENTITY`. A
estratégia de idempotência (hash de conteúdo) chega na Fase 5 com
migração própria.

### 4. Denormalização de `parada`

`Parada` armazena `motivo_descricao` e `planejada` como estavam no
momento do evento, além da FK `motivo_codigo → motivos_parada`. Se o
catálogo de motivos mudar, o evento histórico preserva a verdade do
momento. Drift entre evento e catálogo é sinalizado, não silencioso
(mission §4.2).

### 5. Sem CHECK constraint em `estado`

A validação dos 4 literais (`rodando`, `parado`, `setup`, `manutencao`)
é feita na borda pelo Pydantic (Fase 1). Evolução aditiva de schema
(ADR-002) não pode exigir migração de constraint — adicionar um novo
estado não deve quebrar o banco.

### 6. Turnos como referência fixa

3 turnos de 8h com seed manual: Manhã (06h-14h), Tarde (14h-22h),
Noite (22h-06h). O turno da Noite cruza meia-noite — a instância
pertence à data do seu início. Calendário de produção é derivável
(TODO na Fase 6).

### 7. Agregações de OEE adiadas (Fase 6)

A estrutura de agregação depende das funções de cálculo (D/P/Q/OEE
por máquina×janela) que ainda não existem. Criar a tabela agora seria
pré-otimização com alto risco de retrabalho.

### 8. `DATABASE_URL` via env var com loader `.env` manual

Sem dependência de pydantic-settings — `os.environ.get()` com fallback
para dev. O loader `.env` (~15 linhas) não sobrescreve vars existentes.

## Alternativas consideradas

| Alternativa | Por que não |
|-------------|-------------|
| Tabela normal (sem hypertable) para telemetria | ~200 máquinas × 1–5 s = milhões de rows/dia; hypertable dá particionamento automático e compressão nativa |
| PK surrogate em `telemetria` + unique constraint | TimescaleDB exige que toda constraint única inclua a coluna de particionamento — surrogate exigiria índice extra e não cobre dedup natural |
| CHECK constraint em `estado` | Evolução aditiva de schema quebraria com novos estados; a validação na borda (Pydantic) é mais flexível |
| Normalização estrita de `parada` (só FK) | Perderia a verdade histórica se o catálogo mudar; denormalização é dívida aceita e documentada |
| Tabela `oee_agregado` na Fase 4 | Pré-otimização: a estrutura depende das funções de cálculo que ainda não existem |
| pydantic-settings para config | Dependência nova para funcionalidade trivial (~15 linhas); migrar depois é trivial se a config crescer |

## Consequências

**Positivas:**
- Dados brutos imutáveis — qualquer agregação é reprodutível e auditável
- Hypertable + PK natural = consultas por máquina×janela sem índice extra
- Denormalização de `parada` preserva verdade histórica
- Sem dependências novas (tudo já estava no `pyproject.toml`)

**Negativas:**
- Surrogate ids exigem estratégia de dedup separada (Fase 5)
- Denormalização de `parada` é dívida técnica documentada (drift evento×catálogo)
- Turnos fixos não modelam feriados ou turnos variáveis (suficiente para o skeleton)
- Sem agregações materializadas — consultas de OEE (Fase 6) precisam varrer eventos brutos

**Gatilho de reavaliação:**
- Volume de telemetria exigir compressão ou retention policy → reavaliar chunk interval
- Necessidade de calendário real (feriados, turnos variáveis) → migração de `turnos`
- Performance de consultas de OEE sobre eventos brutos → materializar agregações
