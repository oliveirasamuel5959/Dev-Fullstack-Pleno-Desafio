# Missão

> Documento-constituição do projeto. Toda decisão, ADR e fase do
> [roadmap](roadmap.md) deve estar em conformidade com este arquivo. Se algo
> aqui precisar mudar, muda-se o documento **antes** do código.

## 1. Contexto

Este repositório é a resposta ao **Desafio Técnico — Desenvolvedor(a) Pleno
Full Stack**: projetar a base de software para **ingestão de dados IoT via
MQTT** e um **dashboard operacional de OEE** para a indústria têxtil fictícia
**Malharia Contínua S.A.** (3 galpões, ~200 máquinas, 3 turnos — hoje tudo
anotado em papel/planilha). O enunciado completo está no
[`README.md`](../README.md) e o contrato mínimo em
[`docs/ESPECIFICACAO_TECNICA.md`](../docs/ESPECIFICACAO_TECNICA.md).

O desafio avalia **como pensamos arquitetura**, não um produto pronto:
profundidade de raciocínio > volume de código.

## 2. Missão

> Projetar **e defender** uma base de software _event-driven_ para ingestão de
> telemetria/eventos MQTT e cálculo confiável de OEE, entregue como
> **documentação arquitetural + _walking skeleton_ executável**
> (`docker compose up`), com _harness_ de qualidade real e registro honesto de
> desenvolvimento assistido por IA.

"Defender" é parte da missão: cada escolha de stack, padrão ou escopo cortado
precisa de justificativa escrita (ver §5).

## 3. Critérios de sucesso

Espelham os 8 eixos de avaliação de
[`docs/ENTREGAVEIS.md`](../docs/ENTREGAVEIS.md). A entrega só é considerada
completa quando cada eixo tiver evidência concreta no repositório:

| # | Eixo | Evidência esperada |
|---|------|--------------------|
| 1 | Arquitetura & Modelagem | `docs/ARQUITETURA.md`, diagramas C4 (Contexto + Contêiner), _bounded contexts_ |
| 2 | Event-Driven & MQTT | Topologia de tópicos, QoS por tipo, idempotência, _backpressure_, dead-letter |
| 3 | Monorepo vs. Microsserviços | Decisão explícita com _trade-offs_ em ADR |
| 4 | Estratégia de Nuvem | Design de _deploy_ (diagrama + justificativa de gerenciado vs. self-hosted) |
| 5 | CI/CD | Pipeline real (GitHub Actions) com _quality gates_ |
| 6 | Harness & IA | Testes/linter/_contract test_ executáveis; `docs/AI_ASSISTED.md` preenchido |
| 7 | Dados & OEE | Cálculo correto (produto dos fatores), séries temporais, agregações |
| 8 | Qualidade da Entrega | Coerência decisão↔código, README com instruções reproduzíveis |

## 4. Regras não negociáveis

1. **OEE = Disponibilidade × Performance × Qualidade** — produto, **nunca**
   média. Fórmulas e definições de `docs/ESPECIFICACAO_TECNICA.md` §4 são a
   fonte da verdade.
2. Fatores de OEE sempre em `[0, 1]` (_clamp_), com sinalização explícita de
   dados inconsistentes — nunca absorver erro silenciosamente.
3. Paradas **planejadas** descontam o tempo planejado; **não planejadas**
   descontam a disponibilidade. Não misturar.
4. Tratar (ou documentar como trataria): eventos tardios após fechamento de
   janela, deriva de relógio (`ts_sensor` vs. `ts_ingestao`), duplicatas e
   mensagens fora de ordem, idempotência, _backpressure_ e dead-letter.
5. Contratos de mensagem **versionados** (`telemetria.v1`, `estado.v1`,
   `parada.v1`, `producao.v1`), com evolução que não quebra consumidores.
6. O escopo conceitual da especificação pode ser **estendido**, nunca
   **reduzido**.
7. Os defeitos intencionais em [`data/exemplos-mqtt/`](../data/exemplos-mqtt/)
   (duplicata, fora de ordem, `rpm=0`) existem para exercitar resiliência:
   **tratá-los ou documentá-los — jamais "limpar" os arquivos**.

## 5. Acordos de trabalho

- **Justificar cada decisão** de stack/ferramenta/biblioteca em
  `docs/DECISOES.md`; decisões estruturais viram ADR datado a partir de
  [`docs/adr/000-template.md`](../docs/adr/000-template.md) (mínimo 3).
- **`docs/AI_ASSISTED.md` é atualizado durante o trabalho**, não no final —
  incluindo pelo menos um caso real em que a IA foi contraditada/corrigida.
- Onde pararmos conscientemente, deixar **TODO explícito com o porquê**.
- Documentação de entrega em **pt-BR**; identificadores de contrato já
  estabelecidos em português (`maquina_id`, `motivo_codigo`, ...) são mantidos.
- Histórico de commits **legível**: um commit por unidade lógica de decisão.

## 6. Não-objetivos

- ❌ Funcionalidades de produção (auth, multi-tenant, alerting real, etc.).
- ❌ Integração com fábrica/broker real — o simulador local é suficiente.
- ❌ Pipeline completo de dados — _walking skeleton_ ponta a ponta basta.
- ❌ UI polida — o dashboard precisa ser coerente com a arquitetura, não bonito.
