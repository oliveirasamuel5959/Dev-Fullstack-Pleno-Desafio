# Contratos de Mensagem — JSON Schema

Diretório de contratos versionados para os 4 schemas MQTT do sistema.
Cada arquivo `.schema.json` é gerado automaticamente a partir dos modelos
Pydantic em `src/oee_textil/schemas/mensagens.py` via `model_json_schema()`.

**Fonte da verdade:** os modelos Python. Os JSON Schema aqui são artefatos
exportados para consumidores que não usam Python (simulador externo,
documentação, validação offline).

## Arquivos

| Arquivo | Schema | Descrição |
|---------|--------|-----------|
| `telemetria.v1.schema.json` | `telemetria.v1` | Métricas contínuas de máquina |
| `estado.v1.schema.json` | `estado.v1` | Evento de mudança de estado |
| `parada.v1.schema.json` | `parada.v1` | Evento de parada com motivo |
| `producao.v1.schema.json` | `producao.v1` | Contagem de produção e refugo |

## Regeneração

```bash
uv run python -m oee_textil.schemas.export_json_schema
```

Os arquivos são commitados — mudanças nos schemas Python devem ser
acompanhadas da regeneração dos JSON Schema correspondentes.
