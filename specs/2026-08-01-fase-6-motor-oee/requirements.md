# Requirements — Fase 6: Motor de OEE

> Feature derivada de [`../../specs/roadmap.md`](../../specs/roadmap.md) — Fase 6.
> Conformidade obrigatória com [`../../specs/mission.md`](../../specs/mission.md)
> e [`../../specs/tech-stack.md`](../../specs/tech-stack.md).
> Branch de trabalho: `desafio/samuel-oliveira`.

## 1. Contexto

O roadmap manda: **o cálculo certo, provado com números do enunciado**. Hoje o
repositório tem dados fluindo ponta a ponta (Fase 5): telemetria, estado,
parada e produção são persistidos no TimescaleDB. O que falta é o motor que
transforma esses eventos brutos em OEE — o indicador central do dashboard.

Esta feature implementa funções puras de Disponibilidade, Performance,
Qualidade e OEE, uma camada de repository que consulta o banco e alimenta
essas funções, uma tabela de agregação materializada, e um golden self-check
que valida o cálculo contra o exemplo numérico de
`docs/CONTEXTO_NEGOCIO.md` §2.

**Gate de saída:** `uv run pytest -k oee` verde (inclui caso dourado OEE ≈ 0,79).

## 2. Escopo

### Dentro

- **Funções puras** em `src/oee_textil/services/oee.py`:
  - `disponibilidade(tempo_rodando_s, tempo_planejado_s) -> float`
  - `performance(ciclo_ideal_s, total_produzido, tempo_rodando_s) -> float`
  - `qualidade(produzidas, refugo) -> float`
  - `oee(d, p, q) -> float`
  - Todas com clamp `[0, 1]`, tratamento de divisão por zero, docstrings pt-BR
- **Repository layer** em `src/oee_textil/repositories/oee_repository.py`:
  - `buscar_tempo_planejado(session, maquina_id, inicio, fim)` — duração do
    turno menos paradas planejadas no período
  - `buscar_tempo_rodando(session, maquina_id, inicio, fim)` — tempo planejado
    menos paradas não-planejadas
  - `buscar_producao(session, maquina_id, inicio, fim)` — soma de produzidas
    e refugo
  - `buscar_ciclo_ideal(session, maquina_id)` — da tabela `maquinas`
  - `calcular_oee_maquina(session, maquina_id, inicio, fim)` — orquestra as
    funções acima e retorna dict com D/P/Q/OEE + metadados
- **Tabela `oee_agregado`** + migração Alembic:
  - Colunas: id, maquina_id (FK), janela_inicio, janela_fim, disponibilidade,
    performance, qualidade, oee, unidades_produzidas, unidades_refugo,
    tempo_planejado_s, tempo_rodando_s, ts_calculo
  - UNIQUE (maquina_id, janela_inicio, janela_fim) para upsert idempotente
  - Função `materializar_oee(session, maquina_id, inicio, fim)`
- **Golden self-check** em `tests/test_oee.py`:
  - `test_golden_oee` — caso do `CONTEXTO_NEGOCIO.md` §2: turno 8h (480min),
    60min paradas, ciclo 0.5s, 480.000 produzidas, 24.000 refugo → OEE ≈ 0,79
  - `test_disponibilidade_clamp` — fatores >1.0 são clampados
  - `test_performance_cap` — P > 1.0 cap at 100%
  - `test_divisao_por_zero` — Produzidas=0 → Q=1.0; Planejado=0 → D=0.0
  - `test_oee_produto_nao_media` — OEE = D × P × Q, não (D+P+Q)/3
- **ADR-005**: janelas de agregação (turno 8h + grace 5min) e política de
  late events

### Fora (explicitamente)

- API HTTP / dashboard (Fase 7)
- Cálculo de OEE por linha/galpão (agregação hierárquica — Fase 7)
- Pareto de paradas (Fase 7)
- Buffer de reordenação no consumidor (documentado no ADR-004, não implementado)

## 3. Decisões travadas

### D1 — Funções puras, sem dependência de banco

As 4 funções `disponibilidade`, `performance`, `qualidade`, `oee` recebem
apenas números e retornam floats. Zero imports de SQLAlchemy ou qualquer
infraestrutura. Testáveis com asserts simples, incluindo o golden case
com números hardcoded do enunciado.

### D2 — Repository layer separada

A camada de acesso a dados (`oee_repository.py`) consulta o banco via
SQLAlchemy e retorna dados agregados. Ela **chama** as funções puras —
não o contrário. A separação permite testar o cálculo independentemente
dos dados.

### D3 — Tabela `oee_agregado` materializada

Criar tabela física com UNIQUE (maquina_id, janela_inicio, janela_fim)
para upsert idempotente. A API (Fase 7) consulta esta tabela em vez de
recalcular sobre eventos brutos. Vantagem: resposta rápida para o dashboard,
cálculo auditável (ts_calculo registra quando foi computado).

### D4 — Janela por turno com 5min de grace period

Janela padrão = turno de 8h (manhã 06h–14h, tarde 14h–22h, noite 22h–06h).
Eventos com `ts_sensor` até 5min após `janela_fim` são incluídos na janela
atual. Eventos além disso vão para a janela seguinte. A tolerância de 5min
acomoda clock drift e late arrival moderado sem complexidade de buffer.

### D5 — `ts_sensor` como fonte da verdade temporal

O timestamp do sensor (`ts_sensor`) determina a qual janela o evento
pertence. O `ts_ingestao` (servidor) é metadata para diagnóstico de
clock drift — não afeta o cálculo. Se `ts_sensor` estiver ausente ou
inválido, o evento é ignorado com warning.

### D6 — Clamp explícito com sinalização

Fatores fora de [0, 1] são clampados para o limite mais próximo. O clamp
é acompanhado de warning no stderr com o valor original e o motivo
(ex.: "Performance 1.23 clampado para 1.0 — ciclo ideal subestimado?").
Dados inconsistentes nunca são absorvidos silenciosamente (mission §4.2).

### D7 — Paradas planejadas vs não-planejadas não se misturam

`Disponibilidade` = Tempo Rodando / Tempo Planejado, onde:
- Tempo Planejado = duração do turno − **soma das paradas planejadas**
- Tempo Rodando = Tempo Planejado − **soma das paradas não-planejadas**

A classificação (planejada ou não) vem do campo `planejada` no evento
`parada`, que é um snapshot denormalizado do momento do evento (ADR-003 §4).

### D8 — ADR-005 (ordem cronológica)

ADR-003 (modelagem) e ADR-004 (idempotência) já existem. O próximo número
livre é 005. O roadmap previa ADR-004 para esta fase, mas a numeração real
segue a ordem cronológica das decisões.

## 4. Restrições

- OEE = Disponibilidade × Performance × Qualidade — **produto, nunca média**
  (mission §4.1)
- Fatores sempre em [0, 1] com sinalização explícita de dados inconsistentes
  (mission §4.2)
- Stack conforme tech-stack.md: Python puro para funções, SQLAlchemy para
  repository
- Identificadores em pt-BR: `disponibilidade`, `performance`, `qualidade`,
  `oee`, `tempo_rodando_s`, `tempo_planejado_s`
- Testes das Fases 0–5 devem continuar verdes

## 5. Riscos e observações

- **Golden test vs fórmula da spec**: O exemplo do CONTEXTO_NEGOCIO.md §2
  usa `Performance = (ciclo_ideal × total) / tempo_rodando` com valores
  específicos que resultam em P ≈ 0.952. A spec §4 define a mesma fórmula.
  O teste deve usar os mesmos números.
- **Turno da noite cruza meia-noite**: `22:00` do dia D até `06:00` do dia
  D+1. O cálculo de janela precisa tratar essa borda corretamente.
- **Sem dados reais de parada com duração**: O fixture `estado-parada.ndjson`
  tem transições de estado (parado→rodando) mas o consumidor não calcula
  duração. O repository precisa inferir a duração a partir da diferença entre
  eventos consecutivos de estado.
- **voltas_acumuladas vs unidades_produzidas**: Telemetria tem contador de
  voltas; Produção tem contagem de peças. Para o cálculo de Performance,
  usa-se `unidades_produzidas` da tabela `producao`, não `voltas_acumuladas`.
