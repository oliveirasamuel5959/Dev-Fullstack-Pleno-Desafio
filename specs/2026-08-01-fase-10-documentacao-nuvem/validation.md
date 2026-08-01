# Validation — Fase 10: Documentação final & nuvem

> Como saber que a implementação deu certo e pode ser mergeada.

## Gate documental (saída da Fase)

### 1. `docs/ARQUITETURA.md` existe e contém:

- [ ] Visão geral do estilo arquitetural (Event-Driven + Modular Monolith)
- [ ] Diagrama C4 Contexto (Mermaid) — atores externos + sistema
- [ ] Diagrama C4 Contêiner (Mermaid) — API, Consumidor, Simulador, TimescaleDB, Mosquitto, Dashboard
- [ ] Fluxo de dados descrito (MQTT → Consumidor → DB ← API → Dashboard)
- [ ] _Bounded contexts_ identificados
- [ ] Tabela de decisões-chave com links para ADRs
- [ ] Glossário OEE (disponibilidade, performance, qualidade, turno, parada planejada)

### 2. `docs/TRADEOFFS.md` existe e contém:

- [ ] ≥5 trade-offs documentados
- [ ] Cada trade-off em formato tabela (opção escolhida, alternativa, por que não)
- [ ] Cobre: monorepo vs micro, MQTT self-hosted vs gerenciado, SSE vs WebSocket, banco, linguagem

### 3. `docs/adr/009-estrategia-nuvem-aws.md` existe:

- [ ] Segue o template `docs/adr/000-template.md`
- [ ] Cobre: IoT Core, ECS Fargate, RDS PostgreSQL, CloudWatch, S3, ALB, Route 53
- [ ] Inclui diagrama C4 Deploy (Mermaid)
- [ ] Discute custo, escala e observabilidade

### 4. `infra/terraform/` existe:

- [ ] `main.tf` com provider AWS
- [ ] `iot.tf` com IoT Core topic rules
- [ ] `ecs.tf` com cluster + task definitions
- [ ] `rds.tf` com RDS PostgreSQL instance
- [ ] `variables.tf` + `outputs.tf`
- [ ] `README.md` explicando que é esboço de referência

### 5. `README.md` do fork contém:

- [ ] Como rodar (docker compose, seed, URL do dashboard)
- [ ] Checklist do que foi entregue (referencia ENTREGAVEIS.md)
- [ ] O que ficou de fora + justificativas curtas
- [ ] Estrutura de diretórios do repositório
- [ ] Links para ARQUITETURA.md, DECISOES.md, TRADEOFFS.md, ADRs

### 6. Documentação fechada:

- [ ] `docs/DECISOES.md` tem seção Nuvem preenchida
- [ ] `docs/AI_ASSISTED.md` tem entrada da Fase 10
- [ ] Links cruzados entre todos os documentos funcionam

## Gate executável

```bash
uv run ruff check        # 0 errors
uv run mypy              # 0 errors
uv run pytest            # 138 passed
docker compose up -d     # todos healthy
```

Pipeline CI verde em push na branch `desafio/samuel-oliveira`.

## Critérios de merge

1. Todos os checkboxes da seção "Gate documental" marcados
2. Pipeline CI verde
3. `docs/AI_ASSISTED.md` atualizado com entrada da Fase 10
4. Nenhum arquivo de documentação contém placeholders (TBD, TODO sem justificativa)
