# Makefile — OEE Têxtil (Walking Skeleton)
#
# Entry point unificado para comandos de desenvolvimento.
# Requer: Docker (compose v2), uv, Python 3.14.
#
# Uso:
#   make help        Lista todos os targets
#   make up          Sobe infraestrutura (Mosquitto + TimescaleDB)
#   make test-smoke  Testa conectividade com infraestrutura

.PHONY: help up down ps logs build test-smoke test lint clean \
        migrate migrate-revision migrate-down migrate-history migrate-current \
        seed setup-db

# ── Ajuda ────────────────────────────────────────────────────────────────────

help:  ## Lista os targets disponíveis com descrição
	@grep -E '^[a-zA-Z_-]+:.*## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*## "}; {printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2}'

# ── Infraestrutura (docker compose) ──────────────────────────────────────────

up:  ## Sobe Mosquitto + TimescaleDB em background
	docker compose up -d mosquitto timescaledb
	@echo "Aguardando healthchecks..."
	@sleep 5
	docker compose ps

build:  ## Build da imagem Docker (consumidor + api)
	docker compose build

api:  ## Sobe a API (docker compose up api)
	docker compose up -d api

api-logs:  ## Segue logs da API
	docker compose logs -f api

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

test-docker-sub: ## Roda um comando de mosquitto_sub dentro do container oee-mosquitto
	docker exec -it oee-mosquitto mosquitto_sub -t "smoke/manual/test" -h localhost -p 1883

test-docker-pub: ## Roda um comando de mosquitto_pub dentro do container oee-mosquitto
	docker exec -it oee-mosquitto mosquitto_pub -t "smoke/manual/test" -m "hello oee" -h localhost -p 1883
	
test:  ## Roda todos os testes
	uv run pytest -v

# ── Banco de dados ───────────────────────────────────────────────────────────

migrate:  ## Aplica migracoes pendentes (uv run alembic upgrade head)
	uv run alembic upgrade head

migrate-revision:  ## Gera nova migracao automatica (uso: make migrate-revision MSG="descricao")
	uv run alembic revision --autogenerate -m "$(MSG)"

migrate-down:  ## Reverte a ultima migracao (uv run alembic downgrade -1)
	uv run alembic downgrade -1

migrate-history:  ## Lista historico de migracoes
	uv run alembic history

migrate-current:  ## Mostra a migracao atual do banco
	uv run alembic current

seed:  ## Popula tabelas de catalogo com dados dos CSVs
	uv run python -m oee_textil.seed

setup-db: migrate seed  ## Aplica migracoes + popula tabelas (fluxo completo)
	@echo "Banco pronto: migracoes aplicadas e tabelas populadas."

# ── Qualidade ────────────────────────────────────────────────────────────────

lint:  ## Roda ruff check + ruff format --check + mypy
	uv run ruff check
	uv run ruff format --check
	uv run mypy
