# Plan — Fase 3: Simulador / Publisher

> Execução de [requirements.md](requirements.md). Grupos de tarefas numerados,
> executados **em ordem**; cada grupo termina em verificação + commit próprio.
> Critério de aceite final em [validation.md](validation.md).

## TG1 — Leitura do catálogo e roteamento

- **1.1** Criar `src/oee_textil/simulador/catalogo.py`:
  - Função `carregar_catalogo(data_dir: str) -> dict[str, tuple[str, str]]` que
    lê `maquinas.csv` e retorna `{maquina_id: (galpao, linha)}`.
  - Usar `csv.DictReader` da stdlib. Ignorar linhas começando com `#`.
- **1.2** Criar teste unitário `tests/test_catalogo.py`:
  - Com CSV temporário (tmp_path), verifica que 4 máquinas são carregadas.
  - Verifica que `TEAR-G1-L2-07` retorna `("G1", "L2")`.
  - Verifica que comentários (`#`) são ignorados.
  - Verifica que máquina inexistente levanta `KeyError` (ou retorna `None` —
    decidir no código).
- **Verificação:** `uv run pytest -k catalogo -v` verde.
- **Commit:** `feat: carregador de catálogo de máquinas (CSV → dict)`

## TG2 — Leitura e parsing dos NDJSON

- **2.1** Criar `src/oee_textil/simulador/leitor.py`:
  - Função `carregar_mensagens(data_dir: str) -> list[dict]` que lê os 3
    arquivos NDJSON em ordem (telemetria, estado-parada, producao), ignora
    `//` e linhas vazias, faz `json.loads` em cada linha, e retorna lista
    plana de dicts.
  - Linhas que não são JSON válido → warning no stderr + skip.
- **2.2** Teste unitário `tests/test_leitor.py`:
  - Com arquivos temporários (tmp_path), verifica contagem de linhas.
  - Verifica que comentários `//` são ignorados.
  - Verifica que linhas vazias são ignoradas.
  - Verifica que JSON inválido gera warning mas não interrompe.
- **Verificação:** `uv run pytest -k leitor -v` verde.
- **Commit:** `feat: leitor de NDJSON com filtro de comentários`

## TG3 — Publicador MQTT e CLI principal

- **3.1** Criar `src/oee_textil/simulador/publisher.py`:
  - Função `publicar_mensagens(cliente, mensagens, catalogo, intervalo)` que
    itera sobre a lista de mensagens, valida cada uma via
    `MensagemMQTT.validate_python()`, resolve o tópico a partir do
    `maquina_id` + catálogo, e publica com QoS 1.
  - Logging: `print()` com formato `[fabrica/.../telemetria] telemetria.v1 —
    TEAR-G1-L2-07 @ 2026-03-10T13:45:02`.
  - Mensagens com `maquina_id` ausente do catálogo → warning + skip.
  - Mensagens que falham validação Pydantic → warning + skip.
  - Ctrl+C tratado com `KeyboardInterrupt` → desconecta gracefulmente.
- **3.2** Criar `src/oee_textil/simulador/cli.py`:
  - `argparse.ArgumentParser` com as 6 flags (`--broker-host`, `--broker-port`,
    `--interval`, `--speed`, `--loop`, `--data-dir`).
  - Orquestração: carrega catálogo → carrega mensagens → conecta MQTT →
    publica em loop (se `--loop`) ou uma vez.
- **3.3** Atualizar `src/oee_textil/simulador/__main__.py`:
  - `from oee_textil.simulador.cli import main; main()` para permitir
    `python -m oee_textil.simulador`.
- **3.4** Teste de integração `tests/test_simulador.py`:
  - Com broker Mosquitto rodando: publica sequência de mensagens e verifica
    com `mosquitto_sub` que mensagens chegam nos tópicos esperados.
  - Alternativa: usar cliente paho-mqtt para subscribe + wait.
  - Verifica que `--interval` e `--speed` afetam o tempo de execução.
  - Verifica que Ctrl+C (KeyboardInterrupt) não deixa o broker com conexão
    zumbi.
- **Verificação:** `make up` (garantir broker), `uv run pytest -k simulador -v`
  verde; `mosquitto_sub -t 'fabrica/#' -C 10` mostra mensagens.
- **Commit:** `feat: simulador MQTT — CLI com argparse, publica NDJSONs na
  topologia fabrica/...`

## TG4 — Gates finais e registros

- **4.1** Rodar barra completa: `make lint`, `make test`.
- **4.2** Atualizar `docs/AI_ASSISTED.md`: entrada da Fase 3.
- **4.3** Executar o procedimento de [validation.md](validation.md).
- **Verificação:** todos os gates verdes; simulador publica mensagens
  observáveis no broker.
- **Commit:** `docs: registro AI_ASSISTED (Fase 3)` → push.
