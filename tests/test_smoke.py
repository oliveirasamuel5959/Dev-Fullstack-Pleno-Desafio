"""Smoke test: verifica que o pacote oee_textil e todos os subpacotes
sao importaveis e que o entry point executa.
"""

import subprocess
import sys


def test_pacote_raiz_importavel() -> None:
    """O pacote oee_textil deve ser importavel."""
    import oee_textil

    assert oee_textil.__doc__ is not None


def test_subpacotes_importaveis() -> None:
    """Todos os subpacotes definidos no layout devem ser importaveis."""
    subpacotes = [
        "oee_textil.core",
        "oee_textil.models",
        "oee_textil.schemas",
        "oee_textil.repositories",
        "oee_textil.services",
        "oee_textil.routes",
        "oee_textil.simulador",
    ]
    for nome in subpacotes:
        mod = __import__(nome, fromlist=["__doc__"])
        assert mod.__doc__ is not None, (
            f"Subpacote {nome} nao tem docstring de proposito"
        )


def test_entry_point_executa() -> None:
    """python -m oee_textil deve executar sem erro."""
    result = subprocess.run(
        [sys.executable, "-m", "oee_textil"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"Entry point falhou com stderr: {result.stderr}"
    assert "Hello from dev-fullstack-pleno-desafio!" in result.stdout
