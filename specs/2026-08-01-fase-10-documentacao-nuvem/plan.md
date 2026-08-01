# Plan — Fase 10: Documentação final & nuvem

## TG1 — `docs/ARQUITETURA.md` + C4 diagrams

- Escrever visão geral: estilo **Event-Driven + Modular Monolith**
- **C4 Contexto** (Mermaid): operador do dashboard, sensores IoT, sistema OEE
- **C4 Contêiner** (Mermaid): API FastAPI, Consumidor MQTT, Simulador, TimescaleDB, Mosquitto, Dashboard HTML/JS
- Fluxo de dados: MQTT → Consumidor → TimescaleDB ← API → Dashboard (SSE)
- _Bounded contexts_: Ingestão, Catálogo, OEE, Dashboard
- Tabela de decisões-chave com links para ADRs
- Glossário de termos (OEE, disponibilidade, performance, qualidade, turno, parada planejada)

## TG2 — `docs/TRADEOFFS.md`

- Monorepo vs Microsserviços (ref. ADR-001)
- Mosquitto self-hosted vs AWS IoT Core gerenciado
- SSE vs WebSocket vs Polling (ref. ADR-007)
- PostgreSQL+TimescaleDB vs TimescaleDB Cloud vs Timestream
- Python vs Go/Node para ingestão MQTT
- Docker compose local vs Kubernetes
- Cada trade-off: tabela (opção escolhida, alternativa, por que não)

## TG3 — Cloud AWS + ADR-009 + Terraform

- `docs/adr/009-estrategia-nuvem-aws.md`:
  - AWS IoT Core (MQTT gerenciado), ECS Fargate (containers), RDS PostgreSQL + TimescaleDB, CloudWatch, S3, ALB
  - Diagrama C4 Deploy (Mermaid)
- `infra/terraform/`:
  - `main.tf` (provider AWS), `iot.tf`, `ecs.tf`, `rds.tf`, `variables.tf`, `outputs.tf`, `README.md`
  - Esboço não-applyável documentando a intenção de cada recurso

## TG4 — README do fork

- Badge CI
- Como rodar (docker compose, seed, dashboard URL)
- Checklist do que foi entregue (espelha ENTREGAVEIS.md)
- O que ficou de fora + justificativas
- Estrutura de diretórios
- Links para documentação principal

## TG5 — Fechamento

- Atualizar `docs/DECISOES.md`: seção Nuvem com componentes AWS
- Atualizar `docs/AI_ASSISTED.md`: log Fase 10
- Garantir links cruzados entre todos os documentos
