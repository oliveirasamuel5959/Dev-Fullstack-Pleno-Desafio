-- Init script para TimescaleDB — Fase 2.
-- O banco oee_textil já é criado via POSTGRES_DB env var.
-- A extensão TimescaleDB é habilitada aqui para suporte a hypertables.
CREATE EXTENSION IF NOT EXISTS timescaledb;
