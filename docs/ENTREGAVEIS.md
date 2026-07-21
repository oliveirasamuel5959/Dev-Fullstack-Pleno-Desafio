# Entregáveis e Critérios

Esta é a **régua pública** da avaliação. A pontuação final vai de **0 a 100** e é
a soma ponderada dos eixos abaixo. Cada item é avaliado de forma **objetiva**
(atende / atende parcialmente / não atende) por meio de revisão humana.

> A planilha de correção usada pela banca está na pasta `avaliacao/` deste
> processo (não vem no seu fork). Ela contém os **pesos exatos** de cada eixo e
> critério - de uso interno da banca. Aqui você conhece **quais eixos** são
> avaliados e **como** cada item é pontuado, mas não os pesos numéricos.

---

## Eixos avaliados

| # | Eixo |
|---|------|
| 1 | Arquitetura & Modelagem (C4, bounded contexts, defesa do estilo) |
| 2 | Event-Driven & MQTT (tópicos, QoS, idempotência, backpressure) |
| 3 | Monorepo vs. Microsserviços (decisão + trade-offs) |
| 4 | Estratégia de Nuvem (componentes, escala, custo, observabilidade) |
| 5 | CI/CD (pipeline, quality gates, ambientes, versionamento) |
| 6 | Harness & Dev assistido por IA (testes, contratos, uso de IA, contexto) |
| 7 | Modelagem de Dados & OEE (cálculo correto, time-series, agregações) |
| 8 | Qualidade da Entrega (clareza, coerência decisão↔código, reprodutibilidade) |

---

## O que entregar (checklist)

Marque no seu README o que entregou. **Não** precisa entregar tudo - priorize
profundidade e deixe explícito o que deixou de fora e por quê.

### Documentação (obrigatória)
- [ ] `docs/ARQUITETURA.md` - visão geral, estilo arquitetural escolhido e **por quê**.
- [ ] Diagramas **C4** (ao menos Contexto e Contêiner). Pode ser Mermaid/PlantUML/imagem.
- [ ] `docs/adr/` - pelo menos **3 ADRs** (Architecture Decision Records) usando o template fornecido.
- [ ] `docs/DECISOES.md` - justificativa de **cada** stack/ferramenta/biblioteca escolhida.
- [ ] `docs/TRADEOFFS.md` - monorepo vs. microsserviços, nuvem, mensageria.

### Estrutura base do software (obrigatória - **você constrói do zero**)
- [ ] Organização de pastas/serviços coerente com a arquitetura defendida.
- [ ] _Walking skeleton_ que **roda** (`docker-compose up` ou equivalente) **ou**
      contrato de API + wireframe (ver Especificação Técnica, seção 5).
- [ ] Definição de contratos de mensagem/schema (versionados).
- [ ] Instruções claras de execução no README.

### Nuvem & CI/CD (obrigatória como **design**, opcional como implementação)
- [ ] Diagrama/descrição de _deploy_ em nuvem (provedor à sua escolha).
- [ ] Pipeline de CI/CD (arquivo real de workflow **ou** descrição detalhada).
- [ ] _Quality gates_: lint, testes, _build_, análise de segurança.

### Harness & IA (obrigatória)
- [ ] `docs/AI_ASSISTED.md` preenchido (ver template naquele arquivo).
- [ ] Evidência de _harness_: testes, _linter_, _contract test_ ou _self-check_.
- [ ] Artefatos de otimização de contexto para IA (ex.: `AGENTS.md`,
      `.github/copilot-instructions.md`, `CONVENTIONS.md`, prompts versionados).

---

## Como cada eixo é pontuado (resumo objetivo)

- **Atende (100% do peso do item):** presente, correto e justificado.
- **Parcial (50%):** presente mas incompleto ou sem justificativa clara.
- **Não atende (0%):** ausente ou incorreto.

A quebra fina de cada item (sub-critérios) está na planilha da banca. Aqui
importa: **decisão explícita + justificativa + coerência com o código**.

---

## Formato de entrega

1. Repositório **público** (fork deste) com histórico de commits legível.
2. README do seu fork com: como rodar, o que entregou, o que deixou de fora.
