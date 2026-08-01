# Requirements — Fase 0: Bootstrap do harness

> Feature derivada de [`../../specs/roadmap.md`](../../specs/roadmap.md) — Fase 0.
> Conformidade obrigatória com [`../../specs/mission.md`](../../specs/mission.md)
> e [`../../specs/tech-stack.md`](../../specs/tech-stack.md).
> Branch de trabalho: `desafio/samuel-oliveira`.

## 1. Contexto

O roadmap manda: **quality gates rodando antes de qualquer código de domínio**.
Hoje o repo tem apenas o scaffold do `uv` (`main.py` hello-world, deps
`numpy`/`pandas`) e a constituição em `specs/`. Esta feature entrega o harness
completo (pytest + ruff + mypy + pre-commit), o layout `src/` rigoroso que
todas as fases seguintes vão ocupar, e o ADR-001 que defende a decisão de
organização do código — eixo avaliado ("Monorepo vs. Microsserviços").

## 2. Escopo

### Dentro
- Adicionar dev-deps: `pytest`, `ruff`, `mypy`, `pre-commit` (via `uv add --dev`).
- Configuração de ruff e mypy no `pyproject.toml` (rigor: ver D2).
- Layout `src/` com diretórios de responsabilidade específica (ver D3) +
  pacote importável + smoke test.
- **ADR-001**: monorepo + estilo arquitetural, a partir de
  `docs/adr/000-template.md`.
- `.pre-commit-config.yaml` com ruff e mypy.
- Atualizações de registro: `docs/AI_ASSISTED.md` (entrada da Fase 0) e
  `CLAUDE.md` (seção de toolchain fica desatualizada após esta feature).

### Fora (explicitamente)
- Qualquer código de domínio (contratos MQTT são Fase 1; OEE é Fase 6).
- Docker/compose (Fase 2), CI (Fase 9), nuvem (Fase 10).
- Remover ou "limpar" os defeitos intencionais de `data/exemplos-mqtt/`.

## 3. Decisões travadas

### D1 — Monorepo: um pacote, N entry points
Um único pacote em `src/` com módulos de fronteira explícita; **uma imagem de
container, serviços de compose separados por processo** (api, consumidor,
simulador) nas fases seguintes.
- *Alternativa rejeitada A:* workspace `uv` com pacote por serviço — mais
  cerimônia de build do que um skeleton justifica.
- *Alternativa rejeitada B:* monólito single-process (consumidor MQTT como task
  dentro do FastAPI) — acopla ciclos de vida e enfraquece a narrativa
  event-driven.
- **Esta decisão é o conteúdo do ADR-001** (status: Aceito, data: 2026-07-31).

### D2 — Harness estrito desde o dia um
- `mypy`: `strict = true`, `python_version = 3.14`, resolvendo o pacote em `src/`.
- `ruff`: `target-version = "py314"`, regras estendidas
  `["E", "F", "I", "UP", "B", "SIM", "RUF"]`; `ruff format` adotado.
- Justificativa: quase não há código ainda — adotar rigor agora é barato e
  fortalece o eixo "Harness & IA" (gate objetivo para código humano ou gerado).

### D3 — Layout `src/` rigoroso
Cada diretório tem **uma** responsabilidade, declarada no docstring do seu
`__init__.py`:

```
src/oee_textil/
├── __init__.py
├── main.py            # entry point (reloca o hello-world; `python -m oee_textil`)
├── core/              # config/settings, logging, conexão DB — infra transversal
├── models/            # modelos SQLAlchemy (ORM) — chegam na Fase 4
├── schemas/           # contratos Pydantic v2 (telemetria.v1, ...) — Fase 1
├── repositories/      # acesso a dados (queries) — Fases 4–5
├── services/          # lógica de domínio (ingestão, motor OEE) — Fases 5–6
├── routes/            # routers FastAPI — Fase 7
└── simulador/         # publisher MQTT de demonstração — Fase 3
tests/
└── test_smoke.py      # pacote e subpacotes importáveis
```

Diretórios de fases futuras nascem agora **vazios de código** (só `__init__.py`
com docstring de propósito) — a fronteira é estabelecida antes do código, não
depois. `main.py` da raiz é removido.

### D4 — Pre-commit como gate local
`.pre-commit-config.yaml` com hook oficial do ruff (lint + format) e hook
**local** de mypy (`uv run mypy`), para usar o venv do projeto e a mesma
config do CI futuro.

### D5 — Branch e fluxo
Todo o trabalho do desafio acontece em `desafio/samuel-oliveira`; commits por
grupo de tarefas (ver [plan.md](plan.md)); push ao final da validação.

## 4. Restrições

- Nenhuma regra de [mission.md](../../specs/mission.md) §4 pode ser violada
  (nada se aplica ainda — sem domínio — mas o ADR não pode contraditá-las).
- Stack conforme [tech-stack.md](../../specs/tech-stack.md): apenas ferramentas
  lá listadas entram no `pyproject.toml`.
- Documentação em pt-BR.

## 5. Riscos e observações

- **mypy strict** pode reclamar de código trivial (ex.: falta de anotação de
  retorno em `main()`): resolver anotando, não relaxando a config.
- Hook de mypy do pre-commit: usar `repo: local` com `uv run mypy` — o hook
  oficial criaria um venv paralelo sem as deps do projeto.
- `numpy`/`pandas` já estavam no scaffold: permanecem (serão úteis no motor de
  OEE), mas Fase 0 não os usa.
