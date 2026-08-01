# Validation — Fase 6: Motor de OEE

> Critério de saída do [roadmap](../../specs/roadmap.md): `uv run pytest -k oee`
> verde (inclui o caso dourado ≈ 0,79).

---

## V1 — Funções puras (TG1)

- [ ] **1.1** `src/oee_textil/services/oee.py` existe com 4 funções.
- [ ] **1.2** `disponibilidade(420, 480)` retorna `0.875`.
- [ ] **1.3** `performance(0.5, 480000, 25200)` retorna ≈ `0.952...`.
- [ ] **1.4** `qualidade(480000, 24000)` retorna `0.95`.
- [ ] **1.5** `oee(0.875, 0.952, 0.95)` retorna ≈ `0.79`.
- [ ] **1.6** Clamp superior: P=1.5 → 1.0.
- [ ] **1.7** Clamp inferior: D=-0.5 → 0.0.
- [ ] **1.8** Divisão por zero: `disponibilidade(0, 0)` → 0.0; `qualidade(0, 0)` → 1.0.
- [ ] **1.9** Testes passam:
  ```bash
  uv run pytest -k oee -v
  ```

---

## V2 — Repository + oee_agregado (TG2)

- [ ] **2.1** Modelo `OeeAgregado` existe em `models/oee_agregado.py`.
- [ ] **2.2** Tabela `oee_agregado` existe no banco:
  ```bash
  docker exec oee-timescaledb psql -U oee -d oee_textil -c "\d oee_agregado"
  ```
- [ ] **2.3** `src/oee_textil/repositories/oee_repository.py` existe.
- [ ] **2.4** `calcular_oee_maquina()` retorna dict com D/P/Q/OEE.
- [ ] **2.5** `materializar_oee()` insere/upsert na tabela.
- [ ] **2.6** Testes passam:
  ```bash
  uv run pytest -k oee_repository -v
  ```

---

## V3 — Golden case (TG3)

- [ ] **3.1** `test_golden_oee_≈_079`: `0.78 < OEE < 0.80`.
- [ ] **3.2** `test_paradas_planejadas_descontam_planejado`.
- [ ] **3.3** `test_paradas_nao_planejadas_descontam_disponibilidade`.
- [ ] **3.4** `test_oee_produto_nao_media`: D×P×Q ≠ (D+P+Q)/3.
- [ ] **3.5** Todos os testes `-k oee` passam:
  ```bash
  uv run pytest -k oee -v
  ```

---

## V4 — Gates de qualidade (TG4)

- [ ] **4.1** `make lint` verde.
- [ ] **4.2** `make test` verde (todos os testes).
- [ ] **4.3** Fases 0–5 sem regressão:
  ```bash
  uv run pytest -k "not oee" -v
  ```

---

## V5 — Registros (TG4)

- [ ] **5.1** `docs/adr/005-janelas-agregacao-late-events.md` existe.
- [ ] **5.2** `docs/AI_ASSISTED.md` tem entrada da Fase 6.

---

## Fluxo completo

```bash
make lint && make test
uv run pytest -k oee -v  # golden case ≈ 0.79
```

---

## Resumo

| Verificação | Descrição | Resultado |
|-------------|-----------|-----------|
| V1 | Funções puras D/P/Q/OEE (clamp, div0, golden) | ✅ / ❌ |
| V2 | Repository + tabela oee_agregado + migração | ✅ / ❌ |
| V3 | Golden self-check OEE ≈ 0.79 + edge cases | ✅ / ❌ |
| V4 | Gates de qualidade | ✅ / ❌ |
| V5 | ADR-005 + AI_ASSISTED.md | ✅ / ❌ |

> **Fase 6 fechada quando:** `uv run pytest -k oee` verde **e** golden case
> OEE ≈ 0,79.
> **Fases 0–5 devem continuar verdes.**
