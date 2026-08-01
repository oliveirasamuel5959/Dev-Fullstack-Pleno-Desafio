# Plan — Fase 6: Motor de OEE

> Execução de [requirements.md](requirements.md). Grupos de tarefas numerados,
> executados **em ordem**; cada grupo termina em verificação + commit próprio.
> Critério de aceite final em [validation.md](validation.md).

## TG1 — Funções puras D/P/Q/OEE

- **1.1** Criar `src/oee_textil/services/oee.py` com as 4 funções puras:
  - `disponibilidade(tempo_rodando_s, tempo_planejado_s) -> float`
  - `performance(ciclo_ideal_s, total_produzido, tempo_rodando_s) -> float`
  - `qualidade(produzidas, refugo) -> float`
  - `oee(d, p, q) -> float`
  - Cada função com: docstring, clamp [0,1], tratamento de divisão por zero,
    logging de warning para valores inconsistentes
- **1.2** Criar `tests/test_oee.py` com testes unitários:
  - `test_golden_disponibilidade` — 420/480 = 0.875
  - `test_golden_performance` — (0.5×480000)/(420×60) ≈ 0.952
  - `test_golden_qualidade` — (480000−24000)/480000 = 0.95
  - `test_golden_oee` — 0.875 × 0.952 × 0.95 ≈ 0.79
  - `test_disponibilidade_zero_planejado` — D = 0.0
  - `test_performance_zero_rodando` — P = 0.0
  - `test_qualidade_zero_produzidas` — Q = 1.0
  - `test_clamp_superior` — P = 1.5 → clamp 1.0
  - `test_clamp_inferior` — D = -0.5 → clamp 0.0
  - `test_oee_produto_nao_media` — D×P×Q ≠ (D+P+Q)/3
- **Verificação:** `uv run pytest -k oee -v` verde.
- **Commit:** `feat: funções puras de OEE — Disponibilidade, Performance, Qualidade (Fase 6)`

## TG2 — Repository + tabela oee_agregado

- **2.1** Criar modelo `OeeAgregado` em `src/oee_textil/models/oee_agregado.py`
- **2.2** Registrar no `models/__init__.py`
- **2.3** Gerar migração Alembic: `uv run alembic revision --autogenerate -m "cria tabela oee_agregado"`
- **2.4** Aplicar migração: `make migrate`
- **2.5** Criar `src/oee_textil/repositories/oee_repository.py`:
  - `buscar_tempo_planejado(session, maquina_id, inicio, fim) -> float`
  - `buscar_tempo_rodando(session, maquina_id, inicio, fim) -> float`
  - `buscar_producao(session, maquina_id, inicio, fim) -> tuple[int, int]`
  - `buscar_ciclo_ideal(session, maquina_id) -> float`
  - `calcular_oee_maquina(session, maquina_id, inicio, fim) -> dict`
  - `materializar_oee(session, maquina_id, inicio, fim) -> bool`
- **2.6** Testes em `tests/test_oee_repository.py` (smoke, requer banco):
  - `test_calcular_oee_maquina_com_dados` — insere dados de exemplo e verifica
- **Verificação:** `make migrate && uv run pytest -k oee_repository -v` verde.
- **Commit:** `feat: repository OEE + tabela oee_agregado + migração (Fase 6)`

## TG3 — Golden self-check + edge cases

- **3.1** Expandir `tests/test_oee.py`:
  - `test_golden_oee_≈_079` — assert 0.78 < OEE < 0.80
  - `test_paradas_planejadas_descontam_tempo_planejado`
  - `test_paradas_nao_planejadas_descontam_disponibilidade`
  - `test_turno_noite_cruza_meia_noite`
- **3.2** Rodar a suíte completa de OEE e verificar golden case.
- **Verificação:** `uv run pytest -k oee -v` — golden case ≈ 0.79.
- **Commit:** `test: golden self-check OEE ≈ 0.79 + edge cases (Fase 6)`

## TG4 — ADR-005 + gates finais

- **4.1** Criar `docs/adr/005-janelas-agregacao-late-events.md`
- **4.2** Atualizar `docs/AI_ASSISTED.md`: entrada da Fase 6
- **4.3** Barra completa: `make lint && make test`
- **4.4** Executar [validation.md](validation.md)
- **Verificação:** todos os gates verdes; golden case ≈ 0.79
- **Commit:** `docs: ADR-005 janelas de agregação + registro AI_ASSISTED (Fase 6)` → push
