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

# Copiar codigo fonte (precisa vir antes do sync para instalar o projeto)
COPY src/ src/
COPY data/ data/
COPY migrations/ migrations/
COPY alembic.ini ./

# Instalar dependencias Python + projeto como editavel
RUN uv sync --frozen --no-dev

# Entry point padrao: consumidor
# -u = unbuffered stdout/stderr (necessario para logs no Docker)
ENV PYTHONUNBUFFERED=1
CMD ["/app/.venv/bin/python", "-u", "-m", "oee_textil.services.consumidor"]
