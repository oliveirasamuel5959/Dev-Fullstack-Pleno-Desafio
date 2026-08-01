# Validation — Fase 3: Simulador / Publisher

> Procedimento executável de validação da Fase 3. Rode as verificações abaixo
> **na ordem** após executar todos os grupos de tarefas de [plan.md](plan.md).
> Referência de requisitos: [requirements.md](requirements.md).
> Critério de saída do [roadmap](../../specs/roadmap.md): mensagens visíveis em
> `mosquitto_sub -t 'fabrica/#'`.

---

## V1 — Catálogo de máquinas (TG1)

- [ ] **1.1** `src/oee_textil/simulador/catalogo.py` existe com
  `carregar_catalogo()`.
- [ ] **1.2** Testes unitários passam:
  ```bash
  uv run pytest -k catalogo -v
  ```
- [ ] **1.3** 4 máquinas do CSV são carregadas corretamente (TEAR, URDI,
  TING, RAMA).
- [ ] **1.4** `maquina_id` inexistente é tratado (warning, não crash).

---

## V2 — Leitor de NDJSON (TG2)

- [ ] **2.1** `src/oee_textil/simulador/leitor.py` existe com
  `carregar_mensagens()`.
- [ ] **2.2** Testes unitários passam:
  ```bash
  uv run pytest -k leitor -v
  ```
- [ ] **2.3** Total de linhas JSON carregadas ≥ 12 (4 telemetria + 5
  estado/parada + 3 producao).
- [ ] **2.4** Comentários (`//`) e linhas vazias são ignorados.
- [ ] **2.5** JSON inválido não interrompe o carregamento.

---

## V3 — Publicador e CLI (TG3)

- [ ] **3.1** `src/oee_textil/simulador/publisher.py` existe.
- [ ] **3.2** `src/oee_textil/simulador/cli.py` existe com argparse (6 flags).
- [ ] **3.3** `src/oee_textil/simulador/__main__.py` permite
  `python -m oee_textil.simulador`.
- [ ] **3.4** `--help` funciona e lista todas as flags:
  ```bash
  uv run python -m oee_textil.simulador --help
  ```
- [ ] **3.5** Com broker rodando (`make up`), uma execução sem `--loop`
  publica mensagens e termina:
  ```bash
  uv run python -m oee_textil.simulador --interval 0.1
  ```
- [ ] **3.6** Mensagens são visíveis no broker:
  ```bash
  # Em um terminal:
  mosquitto_sub -t 'fabrica/#' -h localhost -C 5 -v
  # Em outro terminal:
  uv run python -m oee_textil.simulador --interval 0.5
  ```
  Esperado: 5 mensagens com tópicos no formato
  `fabrica/{galpao}/{linha}/{maquina}/{tipo}`.
- [ ] **3.7** `--speed` funciona: com `--speed 10` as mensagens são publicadas
  mais rápido que com `--speed 1`.
- [ ] **3.8** Ctrl+C interrompe gracefulmente (sem traceback, conexão fechada).
- [ ] **3.9** `maquina_id` fora do catálogo gera warning e skip (testar
  temporariamente removendo uma linha do CSV ou com um NDJSON modificado em
  tmp_path).
- [ ] **3.10** Testes de integração passam:
  ```bash
  uv run pytest -k simulador -v
  ```

---

## V4 — Gates de qualidade (TG4)

- [ ] **4.1** `make lint` verde (ruff check + ruff format --check + mypy).
- [ ] **4.2** `make test` verde (todos os testes, incluindo smoke da Fase 2).
- [ ] **4.3** Testes das Fases 0, 1 e 2 continuam passando (sem regressão).
  ```bash
  uv run pytest -k "not simulador and not catalogo and not leitor" -v
  ```

---

## V5 — Registros (TG4)

- [ ] **5.1** `docs/AI_ASSISTED.md` tem entrada da Fase 3 preenchida.
- [ ] **5.2** `Makefile` atualizado com target `simulador` ou `run-sim` (se
  aplicável).

---

## Fluxo completo de validação

```bash
# 1. Garantir infra rodando
make up

# 2. Rodar testes do simulador
uv run pytest -k "catalogo or leitor or simulador" -v

# 3. Teste manual: publicar e observar
uv run python -m oee_textil.simulador --interval 0.2 --speed 2

# 4. Em outro terminal, verificar mensagens
mosquitto_sub -t 'fabrica/#' -C 10 -v

# 5. Barra completa
make lint && make test

# 6. Verificar que Fases 0–2 continuam verdes
uv run pytest -k "not catalogo and not leitor and not simulador" -v

echo "FASE 3: TODOS OS GATES VERDES"
```

---

## Resumo

| Verificação | Descrição | Resultado |
|-------------|-----------|-----------|
| V1 | Catálogo de máquinas (CSV → dict) | ✅ / ❌ |
| V2 | Leitor de NDJSON (3 arquivos, filtro comentários) | ✅ / ❌ |
| V3 | Publicador MQTT + CLI argparse (6 flags, QoS 1) | ✅ / ❌ |
| V4 | Gates de qualidade (ruff, mypy, pytest sem regressão) | ✅ / ❌ |
| V5 | Registros (AI_ASSISTED.md) | ✅ / ❌ |

> **Fase 3 fechada quando:** todas as verificações V1–V5 = ✅ **e** mensagens
> são visíveis em `mosquitto_sub -t 'fabrica/#'`.
> **Fases 0–2 devem continuar verdes**.
