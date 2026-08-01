"""Alembic environment — configuracao de migracoes.

URL do banco via oee_textil.core.config.get_database_url() (env var ou fallback).
Metadata registrada via import de oee_textil.models.
"""

from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

import oee_textil.models  # noqa: F401 — registra todas as tabelas no metadata
from oee_textil.core.config import get_database_url
from oee_textil.core.database import Base

# Alembic Config object
config = context.config

# Logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata para autogenerate
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Migrations offline — gera SQL sem conectar ao banco."""
    url = get_database_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Migrations online — conecta ao banco e executa."""
    # Usar NullPool para migracoes (conexao efemera)
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = get_database_url()
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
