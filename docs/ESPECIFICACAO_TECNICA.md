# Especificação Técnica - MQTT, Modelo de Dados e OEE

Este documento define o **contrato mínimo** que sua arquitetura deve contemplar.
Você pode estender, mas **não reduzir** o escopo conceitual. Nada aqui obriga uma
stack específica.

---

## 1. Ingestão via MQTT

Os sensores/máquinas publicam em um **broker MQTT**. Você define a topologia de
tópicos, mas ela deve ser **hierárquica, previsível e escalável**.

### 1.1 Sugestão de topologia de tópicos (você pode redesenhar - e justificar)

```
fabrica/{galpao}/{linha}/{maquina}/telemetria      # métricas contínuas
fabrica/{galpao}/{linha}/{maquina}/estado          # rodando|parado|setup|manutencao
fabrica/{galpao}/{linha}/{maquina}/parada          # evento de parada com motivo
fabrica/{galpao}/{linha}/{maquina}/producao        # contagem de produção/refugo
```

### 1.2 Requisitos de mensageria que sua arquitetura deve endereçar

- **QoS**: qual nível por tipo de tópico e por quê (0/1/2).
- **Ordenação e duplicidade**: mensagens podem chegar fora de ordem/duplicadas.
  Como garante **idempotência**?
- **Backpressure**: pico de mensagens não pode derrubar o consumidor. Como
  absorve (fila/stream/buffer)?
- **Contrato de mensagem**: _schema_ versionado. Como evolui sem quebrar
  consumidores?
- **Dead-letter**: o que acontece com mensagem inválida?

---

## 2. Contratos de mensagem (exemplos)

Veja payloads completos em [`../data/exemplos-mqtt/`](../data/exemplos-mqtt/).

### 2.1 Telemetria

```json
{
  "schema": "telemetria.v1",
  "maquina_id": "TEAR-G1-L2-07",
  "ts_sensor": "2026-03-10T13:45:02.140Z",
  "rpm": 118.4,
  "voltas_acumuladas": 90418223,
  "temperatura_c": 41.2,
  "vibracao_mm_s": 2.1
}
```

### 2.2 Evento de estado

```json
{
  "schema": "estado.v1",
  "maquina_id": "TEAR-G1-L2-07",
  "ts_sensor": "2026-03-10T13:45:00.000Z",
  "estado": "parado",
  "estado_anterior": "rodando"
}
```

### 2.3 Evento de parada (com motivo)

```json
{
  "schema": "parada.v1",
  "maquina_id": "TEAR-G1-L2-07",
  "ts_sensor": "2026-03-10T13:45:00.000Z",
  "motivo_codigo": "QBR_AGULHA",
  "motivo_descricao": "Quebra de agulha",
  "planejada": false
}
```

### 2.4 Produção / Refugo

```json
{
  "schema": "producao.v1",
  "maquina_id": "TEAR-G1-L2-07",
  "ts_sensor": "2026-03-10T14:00:00.000Z",
  "unidades_produzidas": 21500,
  "unidades_refugo": 900,
  "ordem_producao": "OP-2026-00871"
}
```

---

## 3. Modelo de dados esperado (conceitual)

Sua modelagem deve permitir responder às perguntas do dashboard. Considere ao
menos estas entidades/conceitos:

- **Máquina** (hierarquia: Galpão → Linha → Máquina), com _tempo de ciclo ideal_.
- **Turno** e **calendário de produção** (tempo planejado por período).
- **Eventos de telemetria** (série temporal, alta cardinalidade).
- **Eventos de estado/parada** (com motivo e classificação planejada/não).
- **Produção** (produzido, refugo, ordem de produção).
- **Agregações de OEE** por máquina/linha/galpão × turno/hora/dia.

> Pense na diferença entre **dados brutos (raw/time-series)** e **agregações
> materializadas** para o dashboard. Justifique o banco (ou bancos) escolhido(s):
> relacional, _time-series_, colunar, etc.

---

## 4. Regras de cálculo de OEE (fonte da verdade)

Implemente/documente o cálculo conforme abaixo. Onde não implementar, **descreva**
como faria.

```
Disponibilidade = Tempo Rodando / Tempo Planejado de Produção
Performance     = (Tempo de Ciclo Ideal × Total Produzido) / Tempo Rodando
Qualidade       = Peças Boas / Total Produzido
OEE             = Disponibilidade × Performance × Qualidade
```

Definições:

- **Tempo Planejado de Produção** = duração do turno − paradas **planejadas**.
- **Tempo Rodando** = Tempo Planejado − paradas **não planejadas**.
- **Total Produzido** = `unidades_produzidas` somadas no período.
- **Peças Boas** = `unidades_produzidas − unidades_refugo`.
- **Tempo de Ciclo Ideal** = atributo da máquina (tempo teórico por unidade).

Cuidados que gostaríamos de ver tratados (ou ao menos citados):

- Fatores devem ficar em `[0, 1]`; _clamp_ e sinalização de dados inconsistentes.
- **Janela de agregação** e _late-arriving events_ (evento que chega após o
  fechamento da janela).
- **Fuso e derivação de relógio** (`ts_sensor` vs. `ts_ingestao`).

---

## 5. Backoffice / Dashboard operacional (escopo mínimo)

Não precisa ser bonito. Precisa ser **coerente com a arquitetura**. Entregue ao
menos uma das opções:

- **(A)** Um _walking skeleton_ funcional (mesmo com dados mockados/simulador)
  que mostre OEE e estado ao vivo de pelo menos uma máquina/linha; **ou**
- **(B)** _Wireframe_ + contrato de API (`OpenAPI`/GraphQL SDL) + descrição de
  como o front consumiria os dados em tempo real (WebSocket/SSE/polling) - com
  justificativa.

O dashboard deve contemplar (nem que seja como _mock_/descrição):

1. OEE atual e seus 3 fatores por máquina/linha/galpão.
2. Pareto de motivos de parada.
3. Série temporal de OEE por período.
4. Indicador de máquina parada/anômala agora.

---

## 6. Simulador (recomendado, não obrigatório)

Como não haverá broker real, é **muito bem-visto** entregar um pequeno
**publisher/simulador** que gere mensagens MQTT (ou eventos equivalentes) a
partir dos exemplos em [`../data/exemplos-mqtt/`](../data/exemplos-mqtt/), para
tornar o _skeleton_ executável e demonstrável.
