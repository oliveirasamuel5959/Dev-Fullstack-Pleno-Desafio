# Terraform — OEE Têxtil (esboço de design)

> ⚠️ **Este diretório é um esboço de referência arquitetural, NÃO applyável.**
> Ele documenta a intenção de cada recurso AWS conforme
> [ADR-009](../../docs/adr/009-estrategia-nuvem-aws.md). Para aplicar em uma
> conta AWS real, é necessário:

- [ ] Configurar backend S3 para state remoto (`terraform.backend` em `main.tf`)
- [ ] Criar certificado ACM para o domínio do ALB
- [ ] Mover `db_password` para AWS Secrets Manager
- [ ] Ajustar security groups para restringir ranges de IP
- [ ] Configurar VPC endpoints para ECR + CloudWatch (subnets privadas)
- [ ] Adicionar `aws_cloudwatch_log_group` resources (não incluso no esboço)
- [ ] Configurar IoT Core — registrar certificados X.509 por máquina
- [ ] Adicionar auto-scaling policies para ECS services

## Estrutura

| Arquivo | Conteúdo |
|---------|----------|
| `main.tf` | Provider AWS, VPC, subnets |
| `iot.tf` | IoT Core topic rule → SQS |
| `ecs.tf` | ECS Fargate (cluster, task defs, services, ALB, ECR) |
| `rds.tf` | RDS PostgreSQL, security groups, IAM roles |
| `variables.tf` | Input variables com defaults |
| `outputs.tf` | DNS, endpoints, URLs para CI/CD |

## Estimativa de custo mensal (~200 máquinas, telemetria 5s)

| Recurso | Custo/mês (aprox.) |
|---------|-------------------|
| RDS db.r6g.large Multi-AZ | ~$350 |
| ECS Fargate (3 tasks) | ~$100 |
| ALB | ~$30 |
| IoT Core (200 conexões) | ~$30 |
| S3 + CloudWatch | ~$30 |
| **Total** | **~$540** |

> Valores de referência (us-east-1, on-demand, sem reserved instances).
> Para 1.000 máquinas com telemetria 1s, multiplicar por ~5×.
