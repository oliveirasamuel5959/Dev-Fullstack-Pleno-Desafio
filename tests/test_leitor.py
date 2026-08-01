"""Testes unitarios do leitor de NDJSON."""

from oee_textil.simulador.leitor import _parse_ndjson, carregar_mensagens


def test_carregar_tres_arquivos(tmp_path):
    """Deve carregar os 3 arquivos e retornar lista plana."""
    (tmp_path / "telemetria.ndjson").write_text(
        '{"schema":"telemetria.v1","maquina_id":"T1","ts_sensor":"2026-03-10T13:45:02Z","rpm":100.0,"voltas_acumuladas":1000,"temperatura_c":40.0,"vibracao_mm_s":1.0}\n',
        encoding="utf-8",
    )
    (tmp_path / "estado-parada.ndjson").write_text(
        '{"schema":"estado.v1","maquina_id":"T1","ts_sensor":"2026-03-10T13:45:00Z","estado":"parado","estado_anterior":"rodando"}\n',
        encoding="utf-8",
    )
    (tmp_path / "producao.ndjson").write_text(
        '{"schema":"producao.v1","maquina_id":"T1","ts_sensor":"2026-03-10T14:00:00Z","unidades_produzidas":100,"unidades_refugo":5,"ordem_producao":"OP-001"}\n',
        encoding="utf-8",
    )

    mensagens = carregar_mensagens(tmp_path)

    assert len(mensagens) == 3
    assert mensagens[0]["schema"] == "telemetria.v1"
    assert mensagens[1]["schema"] == "estado.v1"
    assert mensagens[2]["schema"] == "producao.v1"


def test_comentarios_ignorados(tmp_path):
    """Linhas com // devem ser ignoradas."""
    ndjson = tmp_path / "telemetria.ndjson"
    ndjson.write_text(
        "// Este e um comentario\n"
        '{"schema":"telemetria.v1","maquina_id":"T1","ts_sensor":"2026-03-10T13:45:02Z","rpm":100.0,"voltas_acumuladas":1000,"temperatura_c":40.0,"vibracao_mm_s":1.0}\n'
        "// Outro comentario\n",
        encoding="utf-8",
    )

    mensagens = carregar_mensagens(tmp_path)

    assert len(mensagens) == 1


def test_linhas_vazias_ignoradas(tmp_path):
    """Linhas vazias devem ser ignoradas."""
    ndjson = tmp_path / "telemetria.ndjson"
    ndjson.write_text(
        "\n"
        '{"schema":"telemetria.v1","maquina_id":"T1","ts_sensor":"2026-03-10T13:45:02Z","rpm":100.0,"voltas_acumuladas":1000,"temperatura_c":40.0,"vibracao_mm_s":1.0}\n'
        "\n",
        encoding="utf-8",
    )

    mensagens = carregar_mensagens(tmp_path)

    assert len(mensagens) == 1


def test_json_invalido_nao_interrompe(tmp_path, capsys):
    """JSON invalido gera warning mas nao interrompe carregamento."""
    ndjson = tmp_path / "telemetria.ndjson"
    ndjson.write_text(
        '{"schema":"telemetria.v1","maquina_id":"T1","ts_sensor":"2026-03-10T13:45:02Z","rpm":100.0,"voltas_acumuladas":1000,"temperatura_c":40.0,"vibracao_mm_s":1.0}\n'
        "{json invalido}\n"
        '{"schema":"telemetria.v1","maquina_id":"T2","ts_sensor":"2026-03-10T13:45:03Z","rpm":90.0,"voltas_acumuladas":1100,"temperatura_c":40.5,"vibracao_mm_s":1.1}\n',
        encoding="utf-8",
    )

    mensagens = carregar_mensagens(tmp_path)

    assert len(mensagens) == 2
    assert "AVISO" in capsys.readouterr().err


def test_arquivo_ausente(tmp_path, capsys):
    """Arquivo NDJSON ausente gera aviso e retorna lista vazia."""
    mensagens = carregar_mensagens(tmp_path)

    assert len(mensagens) == 0
    stderr = capsys.readouterr().err
    assert "AVISO" in stderr


def test_parse_ndjson_arquivo_inexistente(tmp_path, capsys):
    """Arquivo inexistente retorna lista vazia com aviso."""
    mensagens = _parse_ndjson(tmp_path / "inexistente.ndjson")

    assert mensagens == []
    assert "AVISO" in capsys.readouterr().err


def test_carregar_mensagens_reais():
    """Smoke test: os fixtures reais do projeto devem carregar sem erro."""
    import os

    # Caminho relativo a partir da raiz do repo
    repo_root = os.environ.get("GITHUB_WORKSPACE", ".")
    data_dir = os.path.join(repo_root, "data", "exemplos-mqtt")

    # So executa se o diretorio existir (evita falhar em CI sem fixtures)
    if not os.path.isdir(data_dir):
        import pytest

        pytest.skip("Diretorio data/exemplos-mqtt nao encontrado")

    mensagens = carregar_mensagens(data_dir)

    # Pelo menos 12 linhas JSON validas (4 telemetria + 5 estado/parada + 3 producao)
    assert len(mensagens) >= 12, f"Esperado >=12, obtido {len(mensagens)}"

    schemas = {m["schema"] for m in mensagens if "schema" in m}
    assert "telemetria.v1" in schemas
    assert "estado.v1" in schemas
    assert "parada.v1" in schemas
    assert "producao.v1" in schemas
