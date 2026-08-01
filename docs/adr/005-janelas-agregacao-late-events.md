# ADR-005: Janelas de agregação e política de late events

- **Status:** Aceito
- **Data:** 2026-08-01
- **Decisores:** Samuel Oliveira

## Contexto

A Fase 6 implementa o motor de cálculo de OEE com funções puras, repository
layer e tabela de agregação materializada (`oee_agregado`). O cálculo de OEE
depende de uma **janela de tempo** sobre a qual os eventos são agregados. A
escolha da janela afeta diretamente a granularidade do OEE e a política de
tratamento de eventos que chegam após o fechamento da janela (late events).

Restrições:
- Turnos de 8h (manhã 06h–14h, tarde 14h–22h, noite 22h–06h) — a noite cruza
  meia-noite
- Mensagens podem atrasar, duplicar ou chegar fora de ordem (mission §4.4)
- `ts_sensor` (relógio do sensor) vs `ts_ingestao` (relógio do servidor) —
  deriva de relógio precisa ser considerada
- Volume: ~200 máquinas × 1–5 s de telemetria; eventos de estado/parada/produção
  em frequência menor
- OEE deve ser rastreável e auditável (CONTEXTO_NEGOCIO.md §2)

## Decisão

### 1. Janela primária: turno de 8h

A janela padrão de agregação é o turno de produção (8h):
- Manhã: 06:00–14:00
- Tarde: 14:00–22:00
- Noite: 22:00–06:00 (dia seguinte)

O turno da noite cruza meia-noite — a instância pertence à data do seu início
(22:00 do dia D = turno Noite de D), conforme documentado no modelo `Turno`
(Fase 4).

Esta granularidade é a que o dashboard operacional (Fase 7–8) consulta para
responder "OEE atual por máquina/linha/galpão" e "evolução ao longo do dia".

### 2. Grace period de 5 minutos para late events

Eventos com `ts_sensor` até 5 minutos após `janela_fim` são incluídos na
janela atual. A tolerância de 5 minutos acomoda:
- Clock drift moderado entre sensor e servidor
- Latência de rede na entrega MQTT
- Pequenos atrasos no processamento do consumidor

Eventos com `ts_sensor` além de `janela_fim + 5min` pertencem à janela
seguinte que contém seu `ts_sensor`.

### 3. `ts_sensor` como fonte da verdade temporal

O timestamp do sensor determina a qual janela o evento pertence. O
`ts_ingestao` (servidor) é mantido como metadata para diagnóstico de clock
drift, mas não afeta o cálculo de OEE.

Se `ts_sensor` estiver ausente ou inválido (ex.: futuro distante, anterior
a 1970), o evento é ignorado com warning — nunca incluído em uma janela
incorreta.

### 4. Cálculo sob demanda com materialização

O repository `calcular_oee_maquina()` calcula OEE on-the-fly sobre eventos
brutos. `materializar_oee()` persiste o resultado em `oee_agregado` com
upsert (ON CONFLICT UPDATE), permitindo recálculo idempotente.

A API (Fase 7) consulta `oee_agregado` para respostas rápidas, com fallback
para `calcular_oee_maquina()` se a janela solicitada não estiver materializada.

### 5. Turno como unidade de agregação, não de particionamento

A tabela `oee_agregado` usa `UNIQUE(maquina_id, janela_inicio, janela_fim)`
— a janela é definida por timestamps explícitos, não por `turno_id`. Isso
permite:
- Agregações intra-turno (ex.: OEE por hora) sem mudar o schema
- Turnos customizados ou feriados no futuro sem migração
- A granularidade fica a critério do chamador (API/Fase 7)

O mapeamento `ts_sensor → turno_id` é feito no repository quando necessário.

## Alternativas consideradas

| Alternativa | Por que não |
|-------------|-------------|
| Janela fixa de 1h | Perde o contexto de turno que é a unidade natural de gestão da fábrica |
| Janela deslizante (sliding window) | Complexidade de implementação desproporcional para o skeleton; turnos fixos são suficientes |
| Late events rejeitados (sem grace period) | Perderia dados válidos por latency de rede; 5min é tolerância razoável |
| `ts_ingestao` como fonte da verdade | O momento em que o servidor recebeu não reflete quando o evento ocorreu na fábrica |
| Particionamento por `turno_id` em `oee_agregado` | Engessa a granularidade; timestamps explícitos são mais flexíveis |

## Consequências

**Positivas:**
- Janela por turno alinha o cálculo de OEE com a operação real da fábrica
- Grace period de 5min evita perda de dados por latência sem complexidade
- `ts_sensor` como verdade temporal garante que o OEE reflete o momento real
  do evento
- Materialização com upsert permite recálculo sem duplicação

**Negativas:**
- 5min de grace period é um valor arbitrário — pode precisar de ajuste com
  dados reais
- Turno da noite cruzando meia-noite requer lógica especial de data
- Sem buffer de reordenação no consumidor (ADR-004 documentou mas não
  implementou) — eventos muito fora de ordem podem ser atribuídos à janela
  errada
- Paradas não têm campo de duração — o repository usa estimativa de 5min
  por parada (placeholder, documentado como TODO)

**Gatilho de reavaliação:**
- Volume de late events >5% → aumentar grace period ou implementar buffer
- Necessidade de OEE intra-turno (ex.: por hora) → granularidade já suportada
  pelo schema
- Paradas com duração real (via eventos de estado) → substituir placeholder
  de 5min por cálculo real
