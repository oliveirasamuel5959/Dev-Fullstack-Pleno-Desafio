# Trade-offs

> Decisões com alternativas rejeitadas e justificativas. Complementa
> [`DECISOES.md`](DECISOES.md) (justificativas de stack) e os ADRs (decisões
> estruturais). Cada trade-off documenta **o que escolhemos, o que rejeitamos e
> por quê**.

---

## 1. Monorepo Modular Monolith vs Microsserviços

| | Escolhido | Alternativa |
|---|---|---|
| **Abordagem** | **Modular Monolith** (1 pacote Python, 1 imagem Docker, múltiplos entry points) | Microsserviços (consumidor, API, scheduler OEE como serviços independentes) |
| **Prós** | Deploy simples (`docker compose up`), zero latência interna, refatoração segura, testes integrados fáceis | Escala independente por componente, deploys isolados, falhas contidas |
| **Contras** | Acoplamento no mesmo processo; escala vertical apenas; risco de monolith se tornar _big ball of mud_ | Complexidade operacional (service discovery, distributed tracing, CI/CD multi-serviço), latência de rede, consistência eventual |
| **Por que não microsserviços** | O escopo é um _walking skeleton_ para ~200 máquinas. A modularização interna (`schemas/`, `models/`, `services/`, `routes/`) preserva a opção de extrair serviços no futuro — quando houver necessidade real de escala independente. |
| **Quando reavaliar** | Se o volume de ingestão ultrapassar ~5K msg/s ou se diferentes partes do sistema tiverem requisitos de escala radicalmente diferentes. |
| **Ref.** | [ADR-001](adr/001-monorepo-um-pacote-n-entry-points.md) |

## 2. Mosquitto self-hosted vs AWS IoT Core (MQTT gerenciado)

| | Escolhido (dev) | Alternativa (prod) |
|---|---|---|
| **Abordagem** | **Eclipse Mosquitto** containerizado (dev/local) | **AWS IoT Core** (produção/nuvem) |
| **Prós** | Zero custo, setup em 1 linha de compose, sem dependência de cloud, QoS 0/1/2 completos | MQTT gerenciado: escala automática, HA built-in, integração nativa com AWS (IoT Rule → S3/Kinesis/Lambda), TLS mutual auth |
| **Contras** | Self-hosted: patching, backup, HA manual; single point of failure no compose | Vendor lock-in, custo por mensagem, latência de cold start nas rules, abstrações proprietárias (Device Shadow, Thing Registry) |
| **Por que Mosquitto no skeleton** | O desafio avalia design Event-Driven, não deploy em produção. Mosquitto é o broker MQTT de referência — código aberto, amplamente usado, leve. A migração para IoT Core é trivial: trocar o host/port do cliente MQTT. |
| **Quando migrar** | Em produção com >1 broker ou necessidade de escala elástica. |
| **Ref.** | [ADR-009](adr/009-estrategia-nuvem-aws.md), [tech-stack.md](../specs/tech-stack.md) |

## 3. SSE vs WebSocket vs Polling

| | Escolhido | Alternativa A | Alternativa B |
|---|---|---|---|
| **Abordagem** | **SSE (Server-Sent Events)** | WebSocket | HTTP Polling (`setInterval`) |
| **Prós** | Unidirecional (servidor→cliente), reconexão automática nativa do navegador, HTTP/1.1 simples, sem biblioteca extra | Bidirecional, menor overhead por frame, latência mais baixa | Trivial de implementar, zero complexidade no servidor |
| **Contras** | Só texto (UTF-8), limite de ~6 conexões por domínio (HTTP/1.1), sem suporte nativo a binary frames | Complexidade: handshake upgrade, ping/pong, reconexão manual, estado no servidor | Desperdício de banda, latência proporcional ao intervalo, não escala |
| **Por que SSE** | O dashboard é **somente-leitura** — o operador visualiza, não comanda. SSE é o protocolo mais simples que atende: stream unidirecional com reconexão automática. WebSocket seria complexidade sem benefício. |
| **Ref.** | [ADR-007](adr/007-sse-vs-websocket-polling.md) |

## 4. PostgreSQL + TimescaleDB vs Timestream vs TimescaleDB Cloud

| | Escolhido | Alternativa A | Alternativa B |
|---|---|---|---|
| **Abordagem** | **PostgreSQL 16 + TimescaleDB** (imagem `timescale/timescaledb`) | Amazon Timestream | TimescaleDB Cloud (MST) |
| **Prós** | Mesmo banco para relacional + time-series, hypertables automáticas, SQL completo, sem vendor lock-in, gratuito | Serverless, escala automática, sem gestão de instância, query SQL-like, integração AWS nativa | Gerenciado, sem patching, backups automáticos, suporte oficial |
| **Contras** | Self-hosted: backup, patching, tuning manual; escala vertical apenas | Vendor lock-in total, sem suporte a extensões PostgreSQL, sem chaves estrangeiras, query language proprietária para algumas operações | Custo recorrente, latência extra (cloud), menos controle sobre versões |
| **Por que PG+TimescaleDB** | O mesmo PostgreSQL resolve o núcleo relacional (máquinas, motivos, turnos — com FKs e constraints) **e** as séries temporais (telemetria — com hypertables e compressão nativa). Trocar por Timestream significaria dois bancos ou migração de schema. |
| **Ref.** | [ADR-003](adr/003-modelagem-dados-raw-first-hypertable.md) |

## 5. Python vs Go vs Node.js para ingestão MQTT

| | Escolhido | Alternativa A | Alternativa B |
|---|---|---|---|
| **Abordagem** | **Python 3.14 + aiomqtt** | Go + paho.golang | Node.js + aedes/mqtt.js |
| **Prós** | Stack única (API + consumidor + simulador na mesma linguagem), async nativo (asyncio), ecossistema maduro para dados (pandas, numpy) | Performance superior em I/O, baixo consumo de memória, goroutines leves, binário estático | Mesma linguagem no front e back, async nativo, npm rico |
| **Contras** | GIL limita CPU-bound; memória maior que Go/Rust; startup mais lento | Duas linguagens no projeto, curva de aprendizado, ecossistema de dados menos maduro | Single-threaded, callback hell histórico (mitigado com async/await), dependências pesadas |
| **Por que Python** | O desafio avalia arquitetura, não performance bruta. Com ~200 máquinas publicando a cada 1-5s, o throughput é baixo (~40-200 msg/s). Python com asyncio lida com isso folgadamente. Manter uma linguagem só reduz a carga cognitiva e o custo de manutenção. |
| **Quando reavaliar** | Se o throughput ultrapassar ~5K msg/s ou se a latência de ingestão se tornar crítica. |

## 6. Docker Compose vs Kubernetes (dev/local)

| | Escolhido | Alternativa |
|---|---|---|
| **Abordagem** | **Docker Compose** (4 serviços: mosquitto, timescaledb, consumidor, api) | Kubernetes (minikube/kind/k3s) |
| **Prós** | 1 comando para subir tudo, YAML simples, rede bridge integrada, volumes locais, curva zero | Orquestração real, auto-healing, rollouts, secrets, escala horizontal |
| **Contras** | Sem auto-healing, sem escala horizontal, sem secrets management, manual para CI | Complexidade: ≥3 YAMLs por serviço (deployment, service, configmap), etcd, CNI, DNS interno |
| **Por que Compose** | O _walking skeleton_ tem 4 serviços que cabem em 1 máquina. Compose é a ferramenta certa para dev local e CI. Kubernetes seria overengineering — a complexidade adicionada não entrega valor no escopo do desafio. |
| **Quando reavaliar** | Se o sistema crescer para >5 serviços com requisitos de escala, saúde e segurança diferentes. |

---

## Resumo visual

```
                    Simplicidade ◄──────────────────────────► Escala/Potência
Dev/Local           ─────●─────
Produção/Nuvem      ───────────●─────

                    Python monolito  ◄──────────────────────►  Go microsserviços
Ingestão MQTT       ─────●─────

                    Compose           ◄──────────────────────►  Kubernetes
Orquestração        ─────●─────

                    Mosquitto         ◄──────────────────────►  IoT Core
Broker MQTT         ─────●─────                     (prod) ───●───
```

O esqueleto está todo à esquerda — o eixo da simplicidade. A documentação de
nuvem (ADR-009 + `infra/terraform/`) descreve o caminho para a direita quando
o sistema sair do laboratório.
