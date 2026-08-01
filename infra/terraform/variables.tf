# ── Variáveis ───────────────────────────────────────────────────────────────

variable "aws_region" {
  description = "Região AWS principal"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Ambiente (dev, staging, prod)"
  type        = string
  default     = "prod"
}

variable "db_name" {
  description = "Nome do banco de dados"
  type        = string
  default     = "oee_textil"
}

variable "db_user" {
  description = "Usuário master do RDS"
  type        = string
  sensitive   = true
  default     = "oee_admin"
}

variable "db_password" {
  description = "Senha master do RDS — usar Secrets Manager em produção"
  type        = string
  sensitive   = true
  # TODO: Substituir por aws_secretsmanager_secret_version
}

variable "db_instance_class" {
  description = "Classe da instância RDS"
  type        = string
  default     = "db.r6g.large"
}

variable "acm_certificate_arn" {
  description = "ARN do certificado ACM para HTTPS (ALB)"
  type        = string
  # TODO: Criar certificado via aws_acm_certificate ou importar existente
}
