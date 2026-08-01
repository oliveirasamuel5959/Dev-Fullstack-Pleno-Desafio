# Requirements — Fase 2: Infra local

> Feature derivada de [`../../specs/roadmap.md`](../../specs/roadmap.md) — Fase 2.
> Conformidade obrigatória com [`../../specs/mission.md`](../../specs/mission.md)
> e [`../../specs/tech-stack.md`](../../specs/tech-stack.md).
> Branch de trabalho: `desafio/samuel-oliveira`.

## 1. Contexto

O roadmap manda: **broker e banco sobem com um comando**. Hoje o repositório tem
os schemas Pydantic (Fase 1) e o harness de qualidade (Fase 0), mas nenhuma
infraestrutura de execução. Esta feature cria o `docker-compose.yml` com dois
serviços — Eclipse Mosquitto (broker MQTT) e TimescaleDB (PostgreSQL com extensão
de séries temporais) — configurados com healthchecks reais e um smoke test
programático que valida a conectividade de ambos.

O eixo "Event-Driven & MQTT" da avaliação depende de um broker MQTT real, não
simulado. A partir desta fase, toda a stack de execução está disponível para as
fases seguintes (simulador, consumidor, API).

## 2. Escopo

### Dentro

- **`docker-compose.yml`** na raiz do repositório com dois serviços:
  - `mosquitto` — Eclipse Mosquitto 2, porta `1883`, config injetada via bind
    mount, healthcheck com `mosquitto_sub`.
  - `timescaledb` — TimescaleDB (PostgreSQL 16 + extensão), porta `5432`,
    credenciais `oee`/`oee_dev`/`oee_textil`, volume nomeado `pgdata` para
    persistência, healthcheck com `pg_isready`.
- Rede bridge `oee-network` compartilhada entre os serviços.
- **Config Mosquitto**: `docker/mosquitto/mosquitto.conf` — listener 1883,
  allow_anonymous true, persistence false (explícito; ambiente de dev efêmero).
- **Config TimescaleDB**: script de init `docker/timescaledb/init.sql` opcional
  (criação do banco se necessário).
- **Makefile** com targets principais: `up`, `down`, `ps`, `logs`, `test-smoke`,
  `test`, `lint`, `clean`.
- **Smoke test programático** em `tests/test_smoke.py`:
  - Conecta ao Mosquitto via `paho-mqtt` (pub/sub mínimo — publica uma mensagem
    de teste e verifica recebimento).
  - Conecta ao TimescaleDB via SQLAlchemy (`SELECT 1`).
  - Marcado com `@pytest.mark.smoke` para execução isolada.
- **Dependências novas**: `paho-mqtt`, `psycopg2-binary` (ou `psycopg`), e
  `sqlalchemy` (já previsto no tech-stack, só adicionar ao projeto).

### Fora (explicitamente)

- Dockerfile da aplicação Python (Fase 3+).
- Topologia de tópicos MQTT (simulador define na Fase 3).
- Modelos de dados, Alembic, migrações (Fase 4).
- Consumidor MQTT (Fase 5).
- Cálculo de OEE, API, dashboard (Fases 6–8).

## 3. Decisões travadas

### D1 — Mosquitto anônimo, sem persistência

Listener na porta `1883` (MQTT padrão), `allow_anonymous true`, `persistence
false`. O ambiente é de desenvolvimento local — autenticação e persistência de
sessão são preocupações de staging/produção que não pertencem ao walking skeleton.
O consumidor e o simulador rodam na mesma rede Docker, sem tráfego externo.

### D2 — Volume nomeado para TimescaleDB

Volume `pgdata` mapeado em `/var/lib/postgresql/data`. Garante que dados de
desenvolvimento sobrevivem a `docker compose down` e restarts, o que é útil para
testar o consumidor (Fase 5) sem perder estado entre sessões. O volume pode ser
removido com `docker compose down -v` quando necessário.

### D3 — Smoke test programático, não apenas docker healthcheck

O roadmap define a saída como `docker compose ps` saudável. Vamos além: um smoke
test em pytest que abre conexão real com o broker (pub/sub) e com o banco
(`SELECT 1`). Isso prova que a infra não apenas "subiu", mas está funcionalmente
acessível a partir do código Python — exatamente como o consumidor e a API vão
usá-la. O pytest mark `smoke` permite rodar isolado (`-k smoke`) ou como parte
da suíte completa.

### D4 — Makefile como entry point unificado

Centraliza os comandos mais frequentes em targets documentados:

| Target | Comando |
|--------|---------|
| `make up` | `docker compose up -d` |
| `make down` | `docker compose down` |
| `make ps` | `docker compose ps` |
| `make logs` | `docker compose logs -f` |
| `make test-smoke` | `uv run pytest -k smoke -v` |
| `make test` | `uv run pytest -v` |
| `make lint` | `uv run ruff check && uv run ruff format --check && uv run mypy` |
| `make clean` | `docker compose down -v` |

O Makefile não substitui a documentação — ele a complementa com comandos
executáveis e reproduzíveis. Quem clonar o repositório consegue subir tudo com
`make up && make test-smoke`.

## 4. Restrições

- Nenhuma regra de [mission.md](../../specs/mission.md) §4 pode ser violada.
- Stack conforme [tech-stack.md](../../specs/tech-stack.md): Eclipse Mosquitto,
  TimescaleDB, SQLAlchemy, pytest. `paho-mqtt` e `psycopg2-binary` entram como
  dependências novas (via `uv add`).
- Os containers devem ser acessíveis a partir do host (portas mapeadas) para
  desenvolvimento interativo (ex.: `mosquitto_sub` no host, `psql` no host).
- O `docker-compose.yml` usa sintaxe Compose v3.8+ (compatível com Docker
  Compose v2).
- O Makefile usa GNU Make (disponível no WSL/Linux; Windows users usam WSL).

## 5. Riscos e observações

- **Portas conflitantes**: 1883 (Mosquitto) e 5432 (TimescaleDB) são portas
  padrão. Se o host já tiver um PostgreSQL local na 5432, o mapeamento deve ser
  alterado. Documentar no README como trocar.
- **Cold start do TimescaleDB**: a primeira subida pode demorar alguns segundos
  enquanto o PostgreSQL inicializa. O healthcheck com `pg_isready` cobre isso; o
  smoke test deve ter retry/wait adequado.
- **paho-mqtt vs aiomqtt**: o smoke test pode usar `paho-mqtt` síncrono (mais
  simples para um teste curto). O `aiomqtt` (cliente async) será usado no
  consumidor (Fase 5). Ambos coexistem sem conflito.
- **TimescaleDB em ARM (Apple Silicon)**: a imagem `timescale/timescaledb` tem
  builds multi-arch. Testar com `docker compose up` no ambiente WSL2.
- **Makefile no Windows**: usuários Windows sem WSL precisam usar os comandos
  Docker diretamente. O Makefile documenta os comandos equivalentes em
  comentários.
