# Desafio Técnico - Desenvolvedor(a) Pleno Full Stack

> **Tema:** Arquitetura de base de software para ingestão de dados IoT (MQTT) e
> dashboard operacional de **OEE** em uma indústria **Têxtil**.

Bem-vindo(a)! Este desafio **não** é sobre entregar um produto pronto. É sobre
demonstrar **como você pensa arquitetura de software**: como você estrutura um
projeto _event-driven_, decide entre monorepo e microsserviços, planeja nuvem e
CI/CD, e como você incorpora **desenvolvimento assistido por IA**, **harness de
qualidade** e **otimização de contexto** ao seu fluxo de trabalho.

Você tem **total liberdade de stack, ferramentas e bibliotecas**. A regra é uma
só: **justifique cada decisão**.

---

## 1. Como participar

1. Faça um **fork** deste repositório para a sua conta do GitHub.
2. Trabalhe no seu fork (recomendado: uma branch `desafio/<seu-nome>`).
3. Preencha os _templates_ de documentação em [`docs/`](docs/) e construa a
   **estrutura base** do software (ver [Entregáveis](docs/ENTREGAVEIS.md)).
4. Ao finalizar, deixe o repositório **público** e nos envie o link.
   (Opcional: abra um Pull Request do seu fork para este repositório usando o
   [template de PR](.github/PULL_REQUEST_TEMPLATE.md).)

> ⏱️ **Sugestão:** Priorize profundidade
> de raciocínio sobre volume de código. **Não** queremos que você implemente o
> sistema inteiro.

---

## 2. O que estamos avaliando (transparência total)

A avaliação é **objetiva e ponderada**. Antes da entrevista, seu repositório
passará por uma análise minuciosa,
seguindo critérios públicos. Os eixos avaliados são:

| Eixo | O que observamos |
|------|------------------|
| **Arquitetura & Modelagem** | Diagramas C4, _bounded contexts_, fluxo de dados, escolha e defesa do estilo arquitetural |
| **Event-Driven & MQTT** | Modelagem de tópicos, contratos de mensagem, entrega/QoS, idempotência, _backpressure_ |
| **Monorepo vs. Microsserviços** | Decisão explícita, _trade-offs_, limites de serviço, estratégia de _deploy_ |
| **Estratégia de Nuvem** | Componentes gerenciados vs. self-hosted, escalabilidade, custo, observabilidade |
| **CI/CD** | Pipelines, _quality gates_, estratégia de testes, versionamento, ambientes |
| **Harness & Dev assistido por IA** | Testes, _linters_, _contract tests_, uso documentado de IA, otimização de contexto |
| **Modelagem de Dados & OEE** | Cálculo correto de OEE, _time-series_, granularidade, agregações |
| **Qualidade da Entrega** | Clareza, coerência entre decisão e código, reprodutibilidade |

Os eixos e o método de pontuação estão descritos em
[`docs/ENTREGAVEIS.md`](docs/ENTREGAVEIS.md). Os **pesos numéricos** de cada eixo
são de uso interno da banca. **Não há critérios subjetivos ocultos.**

---

## 3. Ponto de partida

- 📄 **Contexto de negócio:** [`docs/CONTEXTO_NEGOCIO.md`](docs/CONTEXTO_NEGOCIO.md)
- 🔧 **Especificação técnica (MQTT, dados, OEE):** [`docs/ESPECIFICACAO_TECNICA.md`](docs/ESPECIFICACAO_TECNICA.md)
- 📦 **Entregáveis e critérios:** [`docs/ENTREGAVEIS.md`](docs/ENTREGAVEIS.md)
- 🤖 **IA, Harness e otimização de contexto:** [`docs/AI_ASSISTED.md`](docs/AI_ASSISTED.md)
- 🧩 **Amostras de payload MQTT:** [`data/exemplos-mqtt/`](data/exemplos-mqtt/)
- 🏛️ **Registros de decisão (ADR):** [`docs/adr/`](docs/adr/)

---

## 4. Cenário de mentoria

Você não trabalha sozinho. Guarde este cenário - ele será discutido na entrevista
e **não** tem resposta única:

> **Situação.** Um(a) desenvolvedor(a) júnior do seu time, sob pressão de prazo,
> abre um PR que "faz o dashboard funcionar". Para calcular o OEE, ele(a) decidiu
> **somar os três fatores (Disponibilidade + Performance + Qualidade) e dividir
> por 3** - em vez do produto - porque "o número final fica parecido, é mais
> fácil de explicar para o chão de fábrica e economiza tempo". O(a) júnior está
> orgulhoso(a) do resultado, e o **supervisor de produção já elogiou a tela** em
> uma reunião.
>
> Como **você, dev pleno**, conduz essa situação?

Não queremos apenas a correção técnica. Pense em: corretude e credibilidade do
indicador, o prazo real, a motivação do(a) júnior, a expectativa já criada no
cliente interno, e o que você faz **agora** vs. o que você constrói para que o
erro não se repita. Traga o seu raciocínio - a forma como você equilibra esses
fatores diz mais do que a resposta "certa".

---

## 5. Regras

- ✅ **Vale a pena:** documentar o "porquê", desenhar diagramas, deixar TODOs
  explícitos onde você conscientemente parou.
- ✅ **Use IA à vontade** - queremos ver isso. Mas **registre** como usou (ver
  [`docs/AI_ASSISTED.md`](docs/AI_ASSISTED.md)).
- ❌ **Não** copie um projeto pronto sem entender/justificar as decisões.
- ❌ **Não** é necessário conectar a um broker real ou implementar todo o
  pipeline - um _walking skeleton_ que roda é suficiente.

Boa sorte! Estamos mais interessados no **arquiteto** do que no _pixel_. 🚀
