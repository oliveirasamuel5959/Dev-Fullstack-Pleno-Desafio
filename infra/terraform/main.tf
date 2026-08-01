# ── OEE Têxtil — Terraform (esboço de referência) ─────────────────────────
#
# ESTE ARQUIVO É UM ESBOÇO DE DESIGN — NÃO É APPLYÁVEL SEM AJUSTES.
# Ele documenta a intenção de cada recurso AWS conforme ADR-009.
# Para aplicar: configurar backend S3, ajustar security groups, e revisar
# todos os TODO markers.
#
# Provider: AWS us-east-1
# Recursos: IoT Core, ECS Fargate, RDS PostgreSQL, CloudWatch

terraform {
  required_version = ">= 1.9"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  # TODO: Configurar backend S3 para state remoto
  # backend "s3" {
  #   bucket  = "oee-terraform-state"
  #   key     = "prod/terraform.tfstate"
  #   region  = "us-east-1"
  # }
}

provider "aws" {
  region = var.aws_region
}

# ── VPC ────────────────────────────────────────────────────────────────────

resource "aws_vpc" "oee" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = { Name = "oee-vpc" }
}

resource "aws_subnet" "public" {
  count                   = 2
  vpc_id                  = aws_vpc.oee.id
  cidr_block              = "10.0.${count.index}.0/24"
  availability_zone       = data.aws_availability_zones.available.names[count.index]
  map_public_ip_on_launch = true

  tags = { Name = "oee-public-${count.index}" }
}

resource "aws_subnet" "private" {
  count             = 2
  vpc_id            = aws_vpc.oee.id
  cidr_block        = "10.0.${count.index + 10}.0/24"
  availability_zone = data.aws_availability_zones.available.names[count.index]

  tags = { Name = "oee-private-${count.index}" }
}

data "aws_availability_zones" "available" {
  state = "available"
}
