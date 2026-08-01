"""Testes unitarios do carregador de catalogo de maquinas."""

import pytest

from oee_textil.simulador.catalogo import carregar_catalogo


def test_carregar_quatro_maquinas(tmp_path):
    """Catalogo deve conter as 4 maquinas do CSV de exemplo."""
    csv = tmp_path / "maquinas.csv"
    csv.write_text(
        "# Catalogo de maquinas\n"
        "maquina_id,galpao,linha,tipo,tempo_ciclo_ideal_s\n"
        "TEAR-G1-L2-07,G1,L2,tear_circular,0.5\n"
        "URDI-G2-L1-03,G2,L1,urdideira,0.02\n"
        "TING-G3-L1-01,G3,L1,tingimento,3.0\n"
        "RAMA-G3-L2-05,G3,L2,rama_acabamento,1.2\n",
        encoding="utf-8",
    )

    catalogo = carregar_catalogo(tmp_path)

    assert len(catalogo) == 4
    assert catalogo["TEAR-G1-L2-07"] == ("G1", "L2")
    assert catalogo["URDI-G2-L1-03"] == ("G2", "L1")
    assert catalogo["TING-G3-L1-01"] == ("G3", "L1")
    assert catalogo["RAMA-G3-L2-05"] == ("G3", "L2")


def test_comentarios_ignorados(tmp_path):
    """Linhas comecando com # devem ser ignoradas."""
    csv = tmp_path / "maquinas.csv"
    csv.write_text(
        "# Cabecalho comentado\n"
        "maquina_id,galpao,linha,tipo,tempo_ciclo_ideal_s\n"
        "# Maquina de teste\n"
        "TEAR-G1-L2-07,G1,L2,tear_circular,0.5\n"
        "# Outro comentario\n",
        encoding="utf-8",
    )

    catalogo = carregar_catalogo(tmp_path)

    assert len(catalogo) == 1
    assert "TEAR-G1-L2-07" in catalogo


def test_maquina_inexistente(tmp_path):
    """Maquina fora do catalogo deve levantar KeyError no dict."""
    csv = tmp_path / "maquinas.csv"
    csv.write_text(
        "maquina_id,galpao,linha,tipo,tempo_ciclo_ideal_s\n"
        "TEAR-G1-L2-07,G1,L2,tear_circular,0.5\n",
        encoding="utf-8",
    )

    catalogo = carregar_catalogo(tmp_path)

    assert "MAQUINA-INEXISTENTE" not in catalogo
    with pytest.raises(KeyError):
        _ = catalogo["MAQUINA-INEXISTENTE"]


def test_csv_vazio(tmp_path):
    """CSV sem maquinas deve retornar dicionario vazio."""
    csv = tmp_path / "maquinas.csv"
    csv.write_text(
        "maquina_id,galpao,linha,tipo,tempo_ciclo_ideal_s\n",
        encoding="utf-8",
    )

    catalogo = carregar_catalogo(tmp_path)

    assert len(catalogo) == 0


def test_arquivo_inexistente(tmp_path):
    """Deve levantar FileNotFoundError se CSV nao existe."""
    with pytest.raises(FileNotFoundError):
        carregar_catalogo(tmp_path)
