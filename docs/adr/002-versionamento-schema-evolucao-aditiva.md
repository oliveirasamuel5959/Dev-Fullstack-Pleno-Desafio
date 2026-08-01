# ADR-002: Versionamento de schema com evolução aditiva

- **Status:** Aceito
- **Data:** 2026-07-31
- **Decisores:** Samuel Oliveira

## Contexto

O sistema ingere 4 tipos de mensagem MQTT (`telemetria`, `estado`, `parada`,
`producao`), cada uma com seu próprio contrato de dados. A especificação técnica
([ESPECIFICACAO_TECNICA.md](../../docs/ESPECIFICACAO_TECNICA.md) §1.2) exige
que os contratos sejam **versionados** e que a evolução **não quebre
consumidores**. O eixo "Event-Driven & MQTT" da avaliação
([ENTREGAVEIS.md](../../docs/ENTREGAVEIS.md) §2) pontua a estratégia de
versionamento como sub-critério.

O domínio é uma fábrica têxtil com ~200 máquinas e sensores heterogêneos — é
realista esperar que novos campos sejam adicionados aos payloads ao longo do
tempo (ex.: `umidade_percent` na telemetria, `operador_id` na parada). Remover
ou renomear campos quebraria consumidores existentes (simulador, dashboard).

Restrições: os fixtures em `data/exemplos-mqtt/` usam o campo `schema` com valor
`"<nome>.v1"`; o campo já existe e é o discriminador natural.

## Decisão

**Evolução aditiva de schemas com o campo `schema` como discriminador de
versão.**

Regras:

1. **Campo `schema` obrigatório**: todo payload MQTT deve conter
   `"schema": "<tipo>.<versao>"` (ex.: `"telemetria.v1"`). Payload sem o campo
   ou com versão desconhecida é rejeitado na borda (erro de validação →
   dead-letter na Fase 5).

2. **Adição, nunca remoção**: novos campos são adicionados como **opcionais com
   default** (`Optional[T] = None` ou `Field(default=0)`). Campos existentes
   nunca são removidos ou renomeados. O tipo de um campo existente nunca muda.

3. **Nova versão = novo modelo**: quando uma mudança não for compatível com a
   regra 2 (ex.: mudar `rpm` de `float` para `int`, ou tornar obrigatório um
   campo antes opcional), cria-se um novo modelo com `Literal["<nome>.v2"]` e
   adiciona-se à discriminated union `MensagemMQTT`. Consumidores antigos
   continuam recebendo `.v1`; produtores migram para `.v2` no seu ritmo.

4. **Implementação em Pydantic v2**: cada versão é um `BaseModel` com
   `schema: Literal["<nome>.<versao>"]`. A discriminated union
   `TypeAdapter(Annotated[Union[...], Field(discriminator="schema")])` despacha
   automaticamente. A adição de uma nova versão é uma linha na union.

5. **JSON Schema como contrato externo**: os arquivos em `docs/contracts/`
   (Fase 1, TG2) são a manifestação física do contrato. Uma nova versão gera um
   novo arquivo (ex.: `telemetria.v2.schema.json`) sem sobrescrever o anterior.

## Alternativas consideradas

| Alternativa | Prós | Contras | Por que não |
|-------------|------|---------|-------------|
| **Protobuf / Avro com schema registry** | Evolução governada por regras formais do IDL; validação no registro, não na aplicação | Introduz dependência de infraestrutura (Confluent Schema Registry, ou service discovery para protobuf); requer codegen e toolchain extra (protoc, avro-tools) | O stack é Python + JSON + MQTT — adicionar um formato binário e um registry externo para ~200 máquinas é complexidade desproporcional. A simplicidade do JSON + Pydantic atende ao skeleton e escala para o cenário descrito. |
| **Versionamento semântico no tópico MQTT** (`.../telemetria/v1`, `.../telemetria/v2`) | Isolamento total: consumidores assinam apenas a versão que entendem; roteamento via wildcard MQTT | Multiplica tópicos (4 schemas × N versões); simulador/publicador precisa saber qual versão publicar; consumidor precisa assinar múltiplos tópicos | O campo `schema` no payload já resolve a discriminação sem fragmentar a topologia. A topologia de tópicos (`fabrica/.../telemetria`) deve refletir a hierarquia física, não a versão do contrato. |
| **Sem versionamento (confiar no "bom senso")** | Zero cerimônia | Quebra silenciosa: adicionar um campo obrigatório quebra todos os consumidores; remover um campo que o dashboard espera causa erro em runtime | Rejeitado por violar diretamente a missão §4.5 ("contratos versionados"). O eixo Event-Driven & MQTT da avaliação pune a ausência de estratégia. |

## Consequências

- **Positivas:**
  - Consumidores existentes nunca quebram com uma evolução aditiva — um campo
    novo com default é ignorado por código antigo.
  - A discriminated union torna a adição de versões trivial (uma linha no union
    + novo modelo).
  - JSON Schema exportado versionado (`docs/contracts/`) serve como documentação
    imutável e contratual.
  - Alinhado com a stack definida em [tech-stack.md](../../specs/tech-stack.md)
    (Pydantic v2 como validador de borda).

- **Negativas / dívidas assumidas:**
  - Payloads JSON crescem monotonicamente (campos nunca são removidos).
    Mitigação: para ~200 máquinas a 1–5 s, o overhead de campos extras é
    desprezível.
  - A regra "nunca muda o tipo" depende de disciplina humana — o compilador
    (mypy) não impede que alguém mude `rpm: float` para `rpm: int` no mesmo
    modelo. Mitigação: code review + contract test que valida fixtures
    históricos.
  - Não há migração automática entre versões — se `.v2` muda o significado de
    um campo, consumidores antigos leem `.v1` com a semântica antiga.
    Mitigação: mudanças semânticas devem criar nova versão; versões antigas são
    mantidas até que todos os produtores migrem.

- **Como reavaliar no futuro:**
  - Se o número de versões ativas ultrapassar ~3 por schema (ex.: `telemetria`
    com `.v1`, `.v2`, `.v3` simultâneas) → considerar schema registry externo
    ou migração forçada com período de _sunset_.
  - Se um consumidor externo (ex.: sistema de BI) precisar de contratos em
    formato não-JSON → reabrir para avaliar Protobuf/Avro como segundo formato
    de exportação (não substituto).
  - Gatilho concreto: primeira vez que uma evolução **não-aditiva** for
    necessária → este ADR define que isso gera `.v2`; se a frequência de novas
    versões for alta (>1 por mês), reavaliar a estratégia de canais (tópicos
    versionados).
