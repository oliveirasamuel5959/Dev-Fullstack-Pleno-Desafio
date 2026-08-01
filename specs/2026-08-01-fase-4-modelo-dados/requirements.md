# Requirements — Fase 4: Modelo de dados

> Feature derivada de [`../../specs/roadmap.md`](../../specs/roadmap.md) — Fase 4.
> Conformidade obrigatória com [`../../specs/mission.md`](../../specs/mission.md)
> e [`../../specs/tech-stack.md`](../../specs/tech-stack.md).
> Branch de trabalho: `desafio/samuel-oliveira`.

## 1. Contexto

O roadmap manda: **persistência coerente com o modelo conceitual da spec §3**.
Hoje o repositório tem schemas Pydantic (Fase 1), infra local com TimescaleDB
rodando (Fase 2), e um simulador publicando mensagens MQTT (Fase 3). Nenhuma
tabela existe no banco — só a extensão TimescaleDB está habilitada.

Esta feature cria os modelos SQLAlchemy 2.0 para as 7 entidades do domínio,
inicializa o Alembic com a primeira migração, implementa o seed idempotente dos
CSVs de catálogo, e estabelece o módulo `core/` com engine e sessão.

A partir desta fase, o banco está pronto para receber dados do consumidor (Fase 5)
e servir consultas para o motor de OEE (Fase 6) e API (Fase 7).

## 2. Escopo

### Dentro

- **Módulo `core/`** com:
  - `config.py`: loader de `.env` manual (sem pydantic-settings), função
    `get_database_url()` com fallback para dev.
  - `database.py`: `Base` declarativa, `engine` SQLAlchemy, `SessionLocal`
    factory.
- **7 modelos SQLAlchemy 2.0** (`Mapped`, `mapped_column`, `relationship`):
  - `Maquina` — catálogo de máquinas (PK: `maquina_id`)
  - `Turno` — 3 turnos fixos de 8h (PK: `turno_id`)
  - `MotivoParada` — catálogo de motivos (PK: `motivo_codigo`)
  - `Telemetria` — **hypertable** TimescaleDB, PK composta
    `(maquina_id, ts_sensor)`, coluna de particionamento `ts_sensor`
  - `EstadoMaquina` — eventos de mudança de estado (surrogate PK)
  - `Parada` — eventos de parada com motivo (surrogate PK, FK para máquina
    e motivo, denormalizado)
  - `Producao` — eventos de contagem de produção (surrogate PK)
- **`ts_ingestao`** em todas as tabelas de evento com
  `server_default=func.now()` para rastrear deriva de relógio.
- **Alembic init** (`migrations/`) com:
  - `alembic.ini`: `sqlalchemy.url` vazio, `prepend_sys_path = src`
  - `env.py`: `target_metadata = Base.metadata`, URL via `get_database_url()`
  - Primeira migração: 7 tabelas + índices + `create_hypertable` para
    `telemetria` com `by_range('ts_sensor')` via `autocommit_block()`
- **Seed script** (`src/oee_textil/seed.py`):
  - `--data-dir` flag (default `data/exemplos-mqtt`)
  - Lê `maquinas.csv` e `motivos-parada.csv` com `csv.DictReader`
  - Seed fixo de 3 turnos (Manhã/Tarde/Noite)
  - Upsert idempotente com `insert(...).on_conflict_do_nothing()`
- **Makefile**: novos targets `migrate`, `migrate-revision`, `migrate-down`,
  `migrate-history`, `migrate-current`, `seed`, `setup-db`
- **`.env`** (raiz, não versionado) e **`.env.example`** (versionado) com
  `DATABASE_URL`
- **ADR-003**: modelagem de dados (raw-first, hypertable, surrogate ids,
  denormalização, agregações adiadas)

### Fora (explicitamente)

- Seed de eventos NDJSON nas tabelas (é o consumidor, Fase 5)
- Tabela `oee_agregado` (Fase 6)
- `pydantic-settings` (usa `os.environ.get` manual)
- Qualquer lógica de negócio ou cálculo de OEE

## 3. Decisões travadas

### D1 — DATABASE_URL via env var com fallback dev

`get_database_url()` lê `os.environ.get("DATABASE_URL", fallback)` onde o
fallback é a string de conexão dev: `postgresql://oee:oee_dev@localhost:5432/oee_textil`.
O loader `carregar_env()` lê `.env` da raiz sem sobrescrever vars existentes
(ambiente prevalece sobre arquivo). Sem dependência de pydantic-settings ou
python-dotenv — ~15 linhas de Python puro.

### D2 — Hypertable com PK natural (maquina_id, ts_sensor)

TimescaleDB exige que toda constraint única inclua a coluna de particionamento.
A PK `(maquina_id, ts_sensor)` é a chave natural de dedup: um sensor publica
no máximo 1 leitura por tick. O consumidor (Fase 5) usa `ON CONFLICT DO NOTHING`
para idempotência. O índice da PK cobre consultas por máquina×janela sem índice
extra.

### D3 — Surrogate id nos eventos (estado, parada, producao)

Eventos de estado/parada/producao podem ter múltiplas mensagens válidas por
máquina×timestamp (tipos diferentes: `estado.v1` e `parada.v1` no mesmo
instante). Sem PK natural — usa `id BIGINT GENERATED ALWAYS AS IDENTITY`.
A estratégia de dedup (hash de conteúdo) chega na Fase 5 com migração própria.

### D4 — Denormalização de parada

`Parada` armazena `motivo_descricao` e `planejada` como estavam no momento do
evento, além da FK `motivo_codigo → motivos_parada`. Se o catálogo de motivos
mudar (ex.: `SETUP` deixa de ser planejada), o evento histórico preserva a
verdade do momento. Drift entre evento e catálogo é sinalizado, não silencioso
(mission §4.2).

### D5 — Sem CHECK constraint em estado

`EstadoMaquina.estado` aceita qualquer `VARCHAR(20)`. A validação dos 4
literais (`rodando`, `parado`, `setup`, `manutencao`) é feita na borda pelo
Pydantic (Fase 1). Evolução aditiva de schema (ADR-002) não pode exigir
migração de constraint — adicionar um novo estado não deve quebrar o banco.

### D6 — Turnos como referência fixa (seed, sem relationships)

3 turnos de 8h com seed manual: Manhã (06h-14h), Tarde (14h-22h), Noite
(22h-06h). O turno da Noite cruza meia-noite — a instância pertence à data
do seu início. Nenhuma tabela referencia `turnos` ainda (Fase 6 consome).
Calendário de produção é derivável — TODO explícito no docstring.

### D7 — Sem tabela de agregação OEE

Adiado por design para a Fase 6 (motor de OEE). A estrutura de agregação
depende das funções de cálculo (D/P/Q/OEE por máquina×janela) que ainda não
existem. Criar a tabela agora seria pré-otimização com alto risco de
retrabalho.

### D8 — Sem pydantic-settings

Leitura manual de env vars com `os.environ.get()` + loader `.env` de ~15
linhas. Adicionar pydantic-settings agora traria uma dependência para uma
funcionalidade trivial. Se a configuração crescer na Fase 7 (API), migrar é
trivial.

## 4. Restrições

- Nenhuma regra de [mission.md](../../specs/mission.md) §4 pode ser violada.
- Stack conforme [tech-stack.md](../../specs/tech-stack.md): SQLAlchemy 2.0,
  Alembic, TimescaleDB. Nenhuma dependência nova (tudo já está no
  `pyproject.toml`).
- Identificadores em português (`maquina_id`, `motivo_codigo`, `ts_sensor`,
  `ts_ingestao`, etc.).
- `data/exemplos-mqtt/` não pode ser alterado (mission §4.7).
- SQLAlchemy 2.0 style (`Mapped`, `mapped_column`, `DeclarativeBase`).
- mypy strict deve passar sem plugin SQLAlchemy (ignores pontuais com
  comentário quando necessário).
- Testes das Fases 0–3 devem continuar verdes (sem regressão).

## 5. Riscos e observações

- **`create_hypertable` fora de transação**: operações DDL do TimescaleDB
  exigem `autocommit_block()` no Alembic. Padrão documentado, mas requer
  revisão manual da migração autogerada.
- **Import circular**: `core/database.py` importa `core/config.py`; `models/`
  importa `core/database.py`; `migrations/env.py` importa ambos. A ordem de
  imports é segura (config não importa models, database não importa models).
- **mypy × SQLAlchemy**: `Mapped`/`relationship` com forward refs podem exigir
  `# type: ignore[arg-type]` ou `# type: ignore[attr-defined]` pontuais.
  Padrão já usado no projeto.
- **Seed × TimescaleDB**: `telemetria` é hypertable mas não recebe seed de
  eventos — só catálogos (maquinas, motivos, turnos). O consumidor (Fase 5)
  popula as hypertables.
- **`.env` no `.gitignore`**: verificar que `.env` já está listado (linha 87
  do `.gitignore` atual).
- **Turno da Noite cruza meia-noite**: `fim=06:00` do dia seguinte. O cálculo
  de Disponibilidade (Fase 6) precisa tratar essa borda — documentado no
  docstring do modelo.
