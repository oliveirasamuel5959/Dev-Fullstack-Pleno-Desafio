# Requirements — Fase 3: Simulador / Publisher

> Feature derivada de [`../../specs/roadmap.md`](../../specs/roadmap.md) — Fase 3.
> Conformidade obrigatória com [`../../specs/mission.md`](../../specs/mission.md)
> e [`../../specs/tech-stack.md`](../../specs/tech-stack.md).
> Branch de trabalho: `desafio/samuel-oliveira`.

## 1. Contexto

O roadmap manda: **gerar tráfego MQTT real sem fábrica real**. Hoje o repositório
tem o broker Mosquitto rodando (Fase 2), os schemas Pydantic dos 4 tipos de
mensagem (Fase 1), e os fixtures de exemplo em `data/exemplos-mqtt/`. Esta
feature cria uma CLI que lê os arquivos NDJSON de exemplo e os publica como
mensagens MQTT na topologia `fabrica/{galpao}/{linha}/{maquina}/{tipo}`,
simulando o tráfego real de uma fábrica têxtil.

O eixo "Event-Driven & MQTT" da avaliação exige uma topologia de tópicos real e
tráfego observável. A partir desta fase, o consumidor (Fase 5) pode ser testado
com dados realistas fluindo pelo broker.

## 2. Escopo

### Dentro

- **CLI via `argparse`** (stdlib, sem dependências novas) acessível como:
  ```bash
  uv run python -m oee_textil.simulador
  ```
- **Leitura dos 3 arquivos NDJSON** em `data/exemplos-mqtt/`:
  `telemetria.ndjson`, `estado-parada.ndjson`, `producao.ndjson`.
  - Linhas `//` (comentários) e linhas vazias são ignoradas.
  - Cada linha JSON é validada contra o modelo Pydantic correspondente
    (usa `MensagemMQTT.validate_python()` da Fase 1).
  - Linhas inválidas são logadas como warning e puladas (não interrompem
    a simulação).
- **Leitura do catálogo de máquinas** (`maquinas.csv`) como tabela de
  roteamento interna: `maquina_id → (galpao, linha)`. O CSV **não** é
  publicado como mensagem — serve apenas para construir os tópicos MQTT a
  partir do `maquina_id` presente nas mensagens NDJSON.
- **Publicação MQTT** na topologia:
  | Schema | Tópico |
  |--------|--------|
  | `telemetria.v1` | `fabrica/{galpao}/{linha}/{maquina}/telemetria` |
  | `estado.v1` | `fabrica/{galpao}/{linha}/{maquina}/estado` |
  | `parada.v1` | `fabrica/{galpao}/{linha}/{maquina}/parada` |
  | `producao.v1` | `fabrica/{galpao}/{linha}/{maquina}/producao` |
  - QoS 1 (at least once) como padrão para todas as mensagens.
  - Conexão via `paho-mqtt` (já instalado na Fase 2).
- **Flags da CLI**:
  | Flag | Tipo | Default | Descrição |
  |------|------|---------|-----------|
  | `--broker-host` | str | `localhost` | Host do broker MQTT |
  | `--broker-port` | int | `1883` | Porta do broker MQTT |
  | `--interval` | float | `1.0` | Segundos entre mensagens consecutivas |
  | `--speed` | float | `1.0` | Multiplicador de velocidade (2.0 = metade do intervalo) |
  | `--loop` | flag | `false` | Repetir a sequência infinitamente |
  | `--data-dir` | str | `data/exemplos-mqtt` | Diretório com os arquivos NDJSON/CSV |
- **Logging estruturado**: cada mensagem publicada gera um log com tópico,
  maquina_id, schema e timestamp (formato: `[tópico] schema — maquina_id @
  ts_sensor`).
- **Tratamento de descoberta**: se um `maquina_id` das mensagens NDJSON não
  estiver no `maquinas.csv`, logar warning e pular a mensagem.

### Fora (explicitamente)

- Publicação dos CSVs como mensagens MQTT (catálogo vai para o banco na Fase 4).
- Enriquecimento de mensagens com dados do catálogo.
- Modo "real-time por timestamps" (só intervalo fixo + speed multiplier).
- Consumidor, banco de dados, OEE, API (Fases 4–8).

## 3. Decisões travadas

### D1 — argparse, sem dependências novas

A CLI usa `argparse` da stdlib. O escopo é enxuto (6 flags), e adicionar
typer/click seria complexidade desnecessária para um comando de
desenvolvimento. Se a CLI crescer na Fase 5+, migrar para typer é trivial.

### D2 — maquinas.csv como tabela de roteamento (não publicado)

O simulador precisa saber o galpão e a linha de cada máquina para construir
o tópico MQTT (`fabrica/{galpao}/{linha}/{maquina}/...`). Essa informação
está em `maquinas.csv`. O CSV é lido no início da simulação e indexado em
um dicionário `{maquina_id: (galpao, linha)}`. Ele **não** é publicado como
mensagem — os dados de catálogo pertencem ao modelo de dados (Fase 4).

Máquinas no NDJSON que não estejam no catálogo geram warning e são puladas.
Isso evita publicar em tópicos com galpão/linha `None`.

### D3 — Intervalo fixo com speed multiplier

O intervalo entre mensagens é controlado por `time.sleep(effective_interval)`
onde `effective_interval = interval / speed`. Com `--speed 60`, 1 hora de
dados (3600 mensagens a 1/s) é publicada em ~1 minuto.

Esta abordagem é mais simples e previsível que "real-time por timestamps"
(que depende de dados com timestamps sequenciais corretos e falha com
eventos fora de ordem). O consumidor (Fase 5) não depende do ritmo de
publicação — ele processa mensagens conforme chegam.

### D4 — QoS 1 como padrão

Todas as mensagens são publicadas com QoS 1 (at least once). Isso exercita
o tratamento de duplicatas no consumidor (Fase 5) e está alinhado com o
eixo de avaliação "Event-Driven & MQTT". QoS 0 seria simples demais para
demonstrar idempotência; QoS 2 seria overkill para um walking skeleton.

### D5 — O simulador é stateless por design

Cada execução da CLI reconecta ao broker, publica a sequência de mensagens
e desconecta. Não mantém estado entre execuções. O `--loop` simplesmente
reinicia a iteração sobre os arquivos sem reconectar. Isso simplifica o
código e evita bugs de estado.

## 4. Restrições

- Nenhuma regra de [mission.md](../../specs/mission.md) §4 pode ser violada.
  §4.7: os arquivos em `data/exemplos-mqtt/` não podem ser alterados.
- Stack conforme [tech-stack.md](../../specs/tech-stack.md): `paho-mqtt` já
  está instalado (Fase 2). Nenhuma dependência nova.
- O simulador deve funcionar com o broker Mosquitto do `docker compose` (Fase 2).
- A CLI deve poder ser interrompida com Ctrl+C gracefulmente (desconecta do
  broker e fecha).
- Os identificadores de campo em português (`maquina_id`, `motivo_codigo`,
  `ts_sensor`, etc.) são mantidos.

## 5. Riscos e observações

- **Mensagens sem máquina no catálogo**: `producao.ndjson` referencia
  `URDI-G2-L1-03` que está no CSV. `telemetria.ndjson` referencia
  `TEAR-G1-L2-07` e `URDI-G2-L1-03` — ambos no catálogo. `estado-parada.ndjson`
  só referencia `TEAR-G1-L2-07`. Sempre há cobertura completa com os dados
  atuais, mas o código deve tratar o caso de máquina desconhecida.
- **Arquivos com schemas mistos**: `estado-parada.ndjson` contém tanto
  `estado.v1` quanto `parada.v1`. O `MensagemMQTT.validate_python()` da Fase 1
  já despacha corretamente pelo campo `schema`. O simulador só precisa iterar
  sobre as linhas e chamar o validador.
- **Ordem de leitura dos arquivos**: a ordem de publicação é: todas as linhas
  de `telemetria.ndjson`, depois `estado-parada.ndjson`, depois
  `producao.ndjson`. Com `--loop`, repete nessa ordem. Isso pode ser refinado
  no futuro (ex.: interleaving), mas para o walking skeleton é suficiente.
- **QoS 1 e paho-mqtt**: o cliente síncrono do paho-mqtt publica com QoS 1
  sem complexidade adicional — o broker confirma o recebimento.
