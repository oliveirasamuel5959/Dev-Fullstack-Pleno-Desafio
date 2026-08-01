# ── Outputs ─────────────────────────────────────────────────────────────────

output "alb_dns_name" {
  description = "DNS do Application Load Balancer (acesso à API)"
  value       = aws_lb.api.dns_name
}

output "rds_endpoint" {
  description = "Endpoint do RDS PostgreSQL"
  value       = aws_db_instance.oee.endpoint
}

output "ecr_repository_url" {
  description = "URL do repositório ECR para push de imagem Docker"
  value       = aws_ecr_repository.oee.repository_url
}

output "sqs_queue_url" {
  description = "URL da fila SQS de telemetria"
  value       = aws_sqs_queue.telemetria.url
}

output "iot_endpoint" {
  description = "Endpoint do IoT Core para conexão MQTT das máquinas"
  value       = data.aws_iot_endpoint.oee.endpoint_address
}

data "aws_iot_endpoint" "oee" {
  endpoint_type = "iot:Data-ATS"
}
