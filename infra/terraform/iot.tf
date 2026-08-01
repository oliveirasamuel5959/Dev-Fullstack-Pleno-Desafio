# ── AWS IoT Core ────────────────────────────────────────────────────────────
#
# Substitui o Mosquitto self-hosted em produção.
# MQTT gerenciado com TLS mutual auth (certificados X.509 por dispositivo).

# IoT Rule: roteia TODAS as mensagens do tópico fabrica/# para fila SQS
# O consumidor ECS lê da fila (pull) em vez de assinar MQTT direto.
# Isso desacopla ingestão (IoT Core) de processamento (ECS) e permite
# backpressure natural: se o consumidor estiver lento, a fila cresce.

resource "aws_sqs_queue" "telemetria" {
  name                       = "oee-telemetria"
  visibility_timeout_seconds = 30
  message_retention_seconds  = 86400 # 24h — late events têm 1 dia para chegar

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.telemetria_dlq.arn
    maxReceiveCount     = 3
  })

  tags = { Name = "oee-telemetria" }
}

resource "aws_sqs_queue" "telemetria_dlq" {
  name = "oee-telemetria-dlq"
  tags = { Name = "oee-telemetria-dlq" }
}

resource "aws_iot_topic_rule" "fabrica" {
  name        = "oee_fabrica_rule"
  description = "Roteia todas as mensagens MQTT do tópico fabrica/# para SQS"
  sql         = "SELECT * FROM 'fabrica/#'"
  sql_version = "2016-03-23"

  sqs {
    queue_url  = aws_sqs_queue.telemetria.url
    role_arn   = aws_iam_role.iot_sqs.arn
    use_base64 = false
  }
}

resource "aws_iam_role" "iot_sqs" {
  name = "oee-iot-sqs-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = { Service = "iot.amazonaws.com" }
      Action = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy" "iot_sqs" {
  name = "oee-iot-sqs-policy"
  role = aws_iam_role.iot_sqs.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = "sqs:SendMessage"
      Resource = aws_sqs_queue.telemetria.arn
    }]
  })
}
