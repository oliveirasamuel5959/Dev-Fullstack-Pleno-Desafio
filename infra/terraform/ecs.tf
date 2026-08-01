# ── ECS Fargate ────────────────────────────────────────────────────────────
#
# Cluster serverless com 2 serviços: consumidor (1 task) e API (2+ tasks).
# Ambos usam a mesma imagem Docker (ADR-001: imagem única, multi-entrypoint).

resource "aws_ecs_cluster" "oee" {
  name = "oee-textil"
}

# ── Consumidor ──────────────────────────────────────────────────────────────

resource "aws_ecs_task_definition" "consumidor" {
  family                   = "oee-consumidor"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "512"
  memory                   = "1024"
  execution_role_arn       = aws_iam_role.ecs_execution.arn
  task_role_arn            = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([{
    name  = "consumidor"
    image = "${aws_ecr_repository.oee.repository_url}:latest"
    command = [
      "/app/.venv/bin/python", "-u", "-m", "oee_textil.services.consumidor"
    ]
    environment = [
      { name = "DATABASE_URL", value = "postgresql://${var.db_user}:${var.db_password}@${aws_db_instance.oee.endpoint}/${var.db_name}" },
      { name = "MQTT_BROKER_HOST", value = "localhost" }, # Não usado em prod (usa SQS)
      { name = "AWS_SQS_QUEUE_URL", value = aws_sqs_queue.telemetria.url },
    ]
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        awslogs-group         = aws_cloudwatch_log_group.consumidor.name
        awslogs-region        = var.aws_region
        awslogs-stream-prefix = "consumidor"
      }
    }
  }])
}

resource "aws_ecs_service" "consumidor" {
  name            = "oee-consumidor"
  cluster         = aws_ecs_cluster.oee.id
  task_definition = aws_ecs_task_definition.consumidor.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = aws_subnet.private[*].id
    security_groups  = [aws_security_group.ecs.id]
    assign_public_ip = false
  }
}

# ── API ─────────────────────────────────────────────────────────────────────

resource "aws_ecs_task_definition" "api" {
  family                   = "oee-api"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "512"
  memory                   = "1024"
  execution_role_arn       = aws_iam_role.ecs_execution.arn
  task_role_arn            = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([{
    name  = "api"
    image = "${aws_ecr_repository.oee.repository_url}:latest"
    command = [
      "/app/.venv/bin/python", "-u", "-m", "uvicorn",
      "oee_textil.routes.app:app", "--host", "0.0.0.0", "--port", "8000"
    ]
    environment = [
      { name = "DATABASE_URL", value = "postgresql://${var.db_user}:${var.db_password}@${aws_db_instance.oee.endpoint}/${var.db_name}" },
    ]
    portMappings = [{ containerPort = 8000 }]
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        awslogs-group         = aws_cloudwatch_log_group.api.name
        awslogs-region        = var.aws_region
        awslogs-stream-prefix = "api"
      }
    }
  }])
}

resource "aws_ecs_service" "api" {
  name            = "oee-api"
  cluster         = aws_ecs_cluster.oee.id
  task_definition = aws_ecs_task_definition.api.arn
  desired_count   = 2
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = aws_subnet.private[*].id
    security_groups  = [aws_security_group.ecs.id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.api.arn
    container_name   = "api"
    container_port   = 8000
  }
}

# ── ECR (imagem Docker) ─────────────────────────────────────────────────────

resource "aws_ecr_repository" "oee" {
  name = "oee-textil"
}

# ── ALB (Application Load Balancer) ─────────────────────────────────────────

resource "aws_lb" "api" {
  name               = "oee-api-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = aws_subnet.public[*].id
}

resource "aws_lb_target_group" "api" {
  name        = "oee-api-tg"
  port        = 8000
  protocol    = "HTTP"
  vpc_id      = aws_vpc.oee.id
  target_type = "ip"

  health_check {
    path    = "/health"
    matcher = "200"
  }
}

resource "aws_lb_listener" "api" {
  load_balancer_arn = aws_lb.api.arn
  port              = "443"
  protocol          = "HTTPS"
  certificate_arn   = var.acm_certificate_arn # TODO: criar certificate

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.api.arn
  }
}
