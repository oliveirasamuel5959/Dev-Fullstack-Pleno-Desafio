# Makefile — OEE Têxtil (Walking Skeleton)
#
# Entry point unificado para comandos de desenvolvimento.
# Requer: Docker (compose v2), uv, Python 3.14.
#
# Uso:
#   make help        Lista todos os targets
#   make up          Sobe infraestrutura (Mosquitto + TimescaleDB)
#   make test-smoke  Testa conectividade com infraestrutura

.PHONY: help up down ps logs test-smoke test lint clean

# ── Ajuda ────────────────────────────────────────────────────────────────────

help:  ## Lista os targets disponíveis com descrição
	@grep -E '^[a-zA-Z_-]+:.*## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*## "}; {printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2}'

# ── Infraestrutura (docker compose) ──────────────────────────────────────────

up:  ## Sobe Mosquitto + TimescaleDB em background
	docker compose up -d
	@echo "Aguardando healthchecks..."
	@sleep 5
	docker compose ps

down:  ## Para e remove os containers (mantém volume pgdata)
	docker compose down

ps:  ## Mostra status dos containers
	docker compose ps

logs:  ## Segue logs de ambos os serviços
	docker compose logs -f

clean:  ## Para containers e remove volume pgdata (perda total de dados)
	docker compose down -v

# ── Testes ───────────────────────────────────────────────────────────────────

test-smoke:  ## Roda smoke tests de conectividade com infraestrutura
	uv run pytest -m smoke -v

test:  ## Roda todos os testes
	uv run pytest -v

# ── Qualidade ────────────────────────────────────────────────────────────────

lint:  ## Roda ruff check + ruff format --check + mypy
	uv run ruff check
	uv run ruff format --check
	uv run mypy
