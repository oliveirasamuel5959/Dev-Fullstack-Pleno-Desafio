# Requirements — Fase 10: Documentação final & nuvem

> Feature derivada de [`../../specs/roadmap.md`](../../specs/roadmap.md) — Fase 10.
> Branch de trabalho: `desafio/samuel-oliveira`.

## 1. Contexto

Fases 0–9 estão concluídas com pipeline CI verde. A Fase 10 é a última do roadmap:
fecha todos os entregáveis documentais obrigatórios (ARQUITETURA.md, C4, TRADEOFFS.md,
README) e entrega o design de deploy em nuvem que foi adiado ao longo das fases
anteriores.

Hoje o que existe:

| Entregável | Estado |
|------------|--------|
| `docs/ARQUITETURA.md` | ❌ Não existe |
| C4 diagrams | ❌ Não existem |
| `docs/TRADEOFFS.md` | ❌ Não existe |
| `docs/DECISOES.md` | ✅ Criado (Fase 9), pendente seção Nuvem |
| `docs/adr/` | ✅ 8 ADRs (001–008), próximo: 009 |
| `README.md` | ❌ Ainda é o original do desafio |
| `docs/AI_ASSISTED.md` | ✅ Atualizado até Fase 9 |

**Gate de saída:** checklist de `docs/ENTREGAVEIS.md` integralmente referenciado
no README; todos os documentos obrigatórios existem e têm links cruzados.

## 2. Escopo

### Dentro

- **`docs/ARQUITETURA.md`**: visão geral, estilo arquitetural (Event-Driven +
  Modular Monolith), _bounded contexts_, fluxo de dados, glossário OEE
- **C4 diagrams** (Mermaid): Contexto, Contêiner, Deploy (AWS)
- **`docs/TRADEOFFS.md`**: ≥5 trade-offs em formato tabela (monorepo vs micro,
  Mosquitto vs IoT Core, SSE vs WebSocket, PG+Timescale vs Timestream, Python vs
  Go, compose vs K8s)
- **ADR-009**: estratégia de nuvem AWS — IoT Core, ECS Fargate, RDS PostgreSQL
  + TimescaleDB, CloudWatch, S3, ALB, Route 53
- **Terraform esboço** (`infra/terraform/`): main.tf, iot.tf, ecs.tf, rds.tf,
  variables.tf, outputs.tf + README explicando que é referência (não applyável)
- **README do fork**: como rodar, checklist de entregáveis, o que ficou de fora,
  estrutura de diretórios, links para docs
- **Fechamento**: atualizar DECISOES.md (nuvem) + AI_ASSISTED.md (Fase 10)

### Fora

- Deploy real na AWS (custos, conta, domínio)
- Planilha de custos detalhada (estimativa aproximada no ADR-009)
- Terraform apply / state remoto / CI/CD multi-conta
- Observabilidade avançada (X-Ray, tracing distribuído)
- Auth/IAM detalhado (roles, policies por serviço)
- Alertmanager/PagerDuty (fora do escopo da missão §6)

## 3. Decisões

| Decisão | Por quê |
|---------|---------|
| AWS (não GCP ou Azure) | Ecossistema IoT mais maduro (IoT Core), free tier generoso, skills do mercado |
| C4 em Mermaid (não PlantUML ou imagem) | Renderiza nativo no GitHub, versionável em texto, sem dependência externa |
| ECS Fargate (não EKS/Lambda) | Containers sem gestão de nós; walking skeleton não justifica orquestração K8s |
| RDS PostgreSQL + TimescaleDB (não Timestream) | Mesmo modelo de dados do dev local; Timestream exigiria migração de schema |
| IoT Core (não Mosquitto self-hosted em EC2) | MQTT gerenciado elimina patching, escala e HA; custo por mensagem é previsível |
| Terraform esboço (não CDK/Pulumi) | HCL é o padrão de facto para IaC; esboço mostra intenção sem exigir apply |
