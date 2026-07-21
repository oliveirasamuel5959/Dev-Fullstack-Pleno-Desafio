# Contexto de Negócio - Indústria Têxtil & OEE

## 1. A empresa (cenário fictício)

A **Malharia Contínua S.A.** opera um parque fabril com **3 galpões**, cada um
com dezenas de máquinas: **teares circulares**, **urdideiras**, **máquinas de
tingimento** e **ramas de acabamento**. A operação roda em **3 turnos** e a
diretoria quer parar de "achar" e passar a **medir** a eficiência do chão de
fábrica em tempo (quase) real.

Hoje os dados são anotados em papel/planilha por turno. Existem paradas não
registradas, refugo (tecido fora de especificação) subnotificado e nenhuma
visibilidade consolidada. A meta é implantar um sistema que **capture
automaticamente** os sinais das máquinas e **calcule OEE** de forma confiável.

## 2. O indicador central: OEE

**OEE (Overall Equipment Effectiveness)** mede quão bem um recurso produtivo é
utilizado. É o produto de três fatores:

```
OEE = Disponibilidade × Performance × Qualidade
```

| Fator | Fórmula | Explicação no contexto têxtil |
|-------|---------|-------------------------------|
| **Disponibilidade** | `Tempo Rodando / Tempo Planejado de Produção` | Desconta paradas (troca de fio, quebra de agulha, manutenção, _setup_) |
| **Performance** | `(Tempo de Ciclo Ideal × Total Produzido) / Tempo Rodando` | Máquina roda mais devagar que o nominal (fio de baixa qualidade, ajustes) |
| **Qualidade** | `Peças Boas / Total Produzido` | Metragem/rolos dentro da especificação vs. refugo (furos, manchas, gramatura) |

### Exemplo numérico (1 turno de 8h em um tear)

- Tempo planejado: **480 min** (8h). Paradas registradas: **60 min**.
- Tempo rodando: **420 min**.
- Tempo de ciclo ideal: **1 volta / 0,5 s** → ~**2 unidades/s**.
- Total produzido no turno: **480.000 voltas**. Refugo: **24.000 voltas**.

```
Disponibilidade = 420 / 480                         = 0,875  (87,5%)
Performance     = (0,5s × 480.000) / (420×60)s      = 240.000 / 25.200 ≈ 0,952  → limitado a 100% na prática; ajuste ciclo ideal
Qualidade       = (480.000 - 24.000) / 480.000      = 0,95   (95%)
OEE             ≈ 0,875 × 0,95 × 0,95               ≈ 0,79   (79%)
```

> 🎯 O _World Class OEE_ costuma ficar em torno de **85%**. Seu sistema precisa
> tornar esse número **rastreável, auditável e granular** (por máquina, linha,
> turno e período).

## 3. Personas do backoffice

| Persona | Necessidade principal |
|---------|-----------------------|
| **Operador / Líder de turno** | Ver estado ao vivo das máquinas, motivos de parada |
| **Supervisor de produção** | OEE por linha/turno, ranking de perdas (Pareto de paradas) |
| **Gestor industrial** | Tendência de OEE por período, comparação entre galpões |
| **Manutenção** | Alertas de máquina parada/anômala, MTBF/MTTR (bônus) |

## 4. Perguntas que o dashboard operacional deve responder

1. Qual o **OEE atual** de cada máquina/linha/galpão?
2. Onde estão as **maiores perdas** (Disponibilidade, Performance ou Qualidade)?
3. Quais os **principais motivos de parada** no período (Pareto)?
4. Como o OEE **evoluiu** ao longo do dia/semana/mês?
5. Existe alguma máquina **parada ou anômala agora**?

## 5. Restrições e realidade do chão de fábrica

- Conectividade instável: mensagens podem **atrasar, duplicar ou chegar fora de
  ordem**. O sistema precisa ser resiliente a isso.
- Sensores têm **relógios que derivam**; considere _timestamp_ do sensor vs. de
  ingestão.
- Volume: assuma **~200 máquinas**, cada uma publicando a cada **1–5 s**.
  Dimensione pensando em crescimento para 1.000+.
- Nem todo evento é numérico: há **eventos de estado** (rodando/parado/setup) e
  **motivos de parada** (códigos).

> Você **não** precisa resolver tudo isso no código. Precisa **mostrar que
> pensou** nisso na arquitetura e nos ADRs.
