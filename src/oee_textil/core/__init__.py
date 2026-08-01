"""Core — configuracao, logging e infraestrutura transversal.

Responsavel por settings de aplicacao (env vars + .env manual, via
oee_textil.core.config), conexao com banco de dados (engine SQLAlchemy,
via oee_textil.core.database) e logging estruturado.

TODO: logging estruturado (structlog ou logging padrao) — Fase 5+.
"""
