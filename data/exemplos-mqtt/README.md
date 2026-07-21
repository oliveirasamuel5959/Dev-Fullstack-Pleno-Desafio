# Dados de exemplo (MQTT)

Amostras para você tornar o desafio **executável e demonstrável** sem um broker
real. Use-as no seu simulador/publisher ou como _fixtures_ de teste.

| Arquivo | Descrição |
|---------|-----------|
| `telemetria.ndjson` | Métricas contínuas (rpm, temperatura, vibração, voltas). |
| `estado-parada.ndjson` | Eventos de estado e parada. **Contém duplicata e evento fora de ordem** propositais. |
| `producao.ndjson` | Contagem de produção e refugo por janela. |
| `maquinas.csv` | Catálogo de máquinas com `tempo_ciclo_ideal_s` (necessário p/ Performance). |
| `motivos-parada.csv` | Códigos de parada; `planejada` define se desconta Disponibilidade. |

> Os "defeitos" intencionais (duplicidade, _out-of-order_, rpm=0) existem para
> você exercitar **idempotência**, **ordenação** e **detecção de parada**.
> Tratá-los (ou documentar como trataria) conta pontos.
