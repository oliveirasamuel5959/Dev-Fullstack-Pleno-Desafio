"""FastAPI app — API REST do OEE Textil.

Entry point: uv run uvicorn oee_textil.routes.app:app --port 8000
OpenAPI: /docs (Swagger) e /redoc (ReDoc)
"""

from collections.abc import AsyncIterator, Generator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from oee_textil.core.database import SessionLocal


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Logging de startup/shutdown."""
    print("[API] Iniciando servidor...")
    yield
    print("[API] Finalizando servidor...")


app = FastAPI(
    title="OEE Textil API",
    description="API REST do walking skeleton de OEE para Malharia Continua S.A.",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS para dashboard local (Fase 8)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)


def get_db() -> Generator[Any]:
    """Dependency injection: sessao SQLAlchemy por request."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


# Registrar routers
from oee_textil.routes.estado import router as estado_router  # noqa: E402
from oee_textil.routes.oee import router as oee_router  # noqa: E402
from oee_textil.routes.paradas import router as paradas_router  # noqa: E402
from oee_textil.routes.perdas import router as perdas_router  # noqa: E402

app.include_router(oee_router)
app.include_router(paradas_router)
app.include_router(estado_router)
app.include_router(perdas_router)


@app.get("/health")
async def health() -> dict[str, str]:
    """Health check."""
    return {"status": "ok"}
