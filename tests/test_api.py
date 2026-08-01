"""Testes da API REST com TestClient."""

import pytest
from fastapi.testclient import TestClient

from oee_textil.routes.app import app

client = TestClient(app)


def test_health():
    """Health check deve retornar 200."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_docs_abrem():
    """OpenAPI docs devem ser acessiveis."""
    response = client.get("/docs")
    assert response.status_code == 200


def test_openapi_json():
    """OpenAPI JSON schema deve ser gerado."""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    data = response.json()
    assert data["info"]["title"] == "OEE Textil API"
    assert "/api/v1/oee/atual" in data["paths"]
    assert "/api/v1/oee/serie" in data["paths"]
    assert "/api/v1/paradas/pareto" in data["paths"]
    assert "/api/v1/estado/atual" in data["paths"]
    assert "/api/v1/perdas" in data["paths"]


def test_oee_atual_sem_parametros():
    """OEE atual sem parametros retorna lista (pode ser vazia)."""
    response = client.get("/api/v1/oee/atual")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_oee_atual_maquina_inexistente():
    """Maquina inexistente deve retornar 500 (ValueError)."""
    response = client.get("/api/v1/oee/atual?maquina_id=MAQUINA-X")
    assert response.status_code in (404, 500)


def test_oee_serie_sem_maquina():
    """Serie sem maquina_id deve retornar 422 (validacao)."""
    response = client.get("/api/v1/oee/serie")
    assert response.status_code == 422


def test_paradas_pareto_sem_parametros():
    """Pareto sem parametros retorna 200 (default 7 dias)."""
    response = client.get("/api/v1/paradas/pareto")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data


def test_estado_atual():
    """Estado atual retorna 200 com contadores."""
    response = client.get("/api/v1/estado/atual")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "rodando" in data
    assert "parado" in data


def test_perdas_sem_maquina():
    """Perdas sem maquina_id retorna 422."""
    response = client.get("/api/v1/perdas")
    assert response.status_code == 422


@pytest.mark.smoke
def test_oee_atual_com_dados():
    """OEE atual para maquina existente retorna dados (requer DB com seed)."""
    response = client.get("/api/v1/oee/atual?maquina_id=TEAR-G1-L2-07")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["maquina_id"] == "TEAR-G1-L2-07"
    assert "fatores" in data[0]
    assert "oee" in data[0]
    assert 0.0 <= data[0]["oee"] <= 1.0
