# ── RDS PostgreSQL + TimescaleDB ────────────────────────────────────────────
#
# Banco gerenciado com extensão TimescaleDB habilitada.
# Multi-AZ para HA em produção.

resource "aws_db_instance" "oee" {
  identifier     = "oee-textil"
  engine         = "postgres"
  engine_version = "16.3"
  instance_class = var.db_instance_class

  db_name  = var.db_name
  username = var.db_user
  password = var.db_password

  allocated_storage     = 100
  storage_type          = "gp3"
  storage_encrypted     = true
  publicly_accessible   = false
  multi_az              = true
  db_subnet_group_name  = aws_db_subnet_group.oee.name
  vpc_security_group_ids = [aws_security_group.rds.id]

  backup_retention_period = 7
  backup_window           = "03:00-04:00"
  maintenance_window      = "sun:04:00-sun:05:00"

  enabled_cloudwatch_logs_exports = ["postgresql"]

  tags = {
    Name        = "oee-textil"
    Environment = var.environment
  }
}

resource "aws_db_subnet_group" "oee" {
  name       = "oee-db-subnet"
  subnet_ids = aws_subnet.private[*].id
}

# ── Security Groups ─────────────────────────────────────────────────────────

resource "aws_security_group" "rds" {
  name        = "oee-rds-sg"
  description = "Permite trafego PostgreSQL das tasks ECS"
  vpc_id      = aws_vpc.oee.id

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.ecs.id]
  }
}

resource "aws_security_group" "ecs" {
  name        = "oee-ecs-sg"
  description = "Tasks ECS"
  vpc_id      = aws_vpc.oee.id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "alb" {
  name        = "oee-alb-sg"
  description = "ALB publico"
  vpc_id      = aws_vpc.oee.id

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# ── IAM (execução e task) ───────────────────────────────────────────────────

resource "aws_iam_role" "ecs_execution" {
  name = "oee-ecs-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = { Service = "ecs-tasks.amazonaws.com" }
      Action = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_execution" {
  role       = aws_iam_role.ecs_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role" "ecs_task" {
  name = "oee-ecs-task-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = { Service = "ecs-tasks.amazonaws.com" }
      Action = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy" "ecs_task_sqs" {
  name = "oee-ecs-sqs-policy"
  role = aws_iam_role.ecs_task.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = [
        "sqs:ReceiveMessage",
        "sqs:DeleteMessage",
        "sqs:GetQueueAttributes",
      ]
      Resource = aws_sqs_queue.telemetria.arn
    }]
  })
}
