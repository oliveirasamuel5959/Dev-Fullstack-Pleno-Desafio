# OEE Têxtil — Walking Skeleton
# Imagem única, multi-entrypoint (ADR-001).
#
# Uso:
#   docker compose build consumidor
#   docker compose up -d
#
# Entry points (sobrescrever com docker compose `command:`):
#   python -m oee_textil.services.consumidor   (default)
#   python -m oee_textil.simulador
#   python -m oee_textil.seed

FROM python:3.14-slim

WORKDIR /app

# Instalar dependencias do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Instalar uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copiar manifestos de dependencia primeiro (cache layer)
COPY pyproject.toml uv.lock README.md ./

# Instalar dependencias Python
RUN uv sync --frozen --no-dev

# Copiar codigo fonte
COPY src/ src/
COPY data/ data/
COPY migrations/ migrations/
COPY alembic.ini ./

# Entry point padrao: consumidor
CMD ["uv", "run", "python", "-m", "oee_textil.services.consumidor"]
