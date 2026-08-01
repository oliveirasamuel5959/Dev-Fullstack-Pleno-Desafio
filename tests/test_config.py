"""Testes unitarios do modulo core.config."""

import os

from oee_textil.core.config import DEFAULT_DATABASE_URL, carregar_env, get_database_url


def test_default_url_sem_env(monkeypatch):
    """Sem DATABASE_URL no ambiente, retorna o fallback de dev."""
    monkeypatch.delenv("DATABASE_URL", raising=False)
    url = get_database_url()
    assert url == DEFAULT_DATABASE_URL


def test_env_var_sobrescreve(monkeypatch):
    """DATABASE_URL no ambiente prevalece sobre o default."""
    custom = "postgresql://user:pass@host:5432/db"
    monkeypatch.setenv("DATABASE_URL", custom)
    url = get_database_url()
    assert url == custom


def test_carregar_env_le_arquivo(tmp_path, monkeypatch):
    """.env em tmp_path deve ser carregado no os.environ."""
    env_file = tmp_path / ".env"
    env_file.write_text(
        "# comentario\n"
        "DATABASE_URL=postgresql://test:test@localhost:5432/test_db\n"
        "MQTT_HOST=broker.local\n",
        encoding="utf-8",
    )
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("MQTT_HOST", raising=False)

    carregar_env(env_file)

    assert os.environ["DATABASE_URL"] == "postgresql://test:test@localhost:5432/test_db"
    assert os.environ["MQTT_HOST"] == "broker.local"


def test_carregar_env_nao_sobrescreve_existente(tmp_path, monkeypatch):
    """Variavel ja definida no ambiente NAO deve ser sobrescrita pelo .env."""
    env_file = tmp_path / ".env"
    env_file.write_text(
        "DATABASE_URL=postgresql://arquivo:pass@localhost/db\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("DATABASE_URL", "postgresql://ambiente:pass@localhost/db")

    carregar_env(env_file)

    assert os.environ["DATABASE_URL"] == "postgresql://ambiente:pass@localhost/db"


def test_carregar_env_arquivo_inexistente_noop(tmp_path, monkeypatch):
    """.env inexistente nao deve levantar erro."""
    monkeypatch.delenv("DATABASE_URL", raising=False)
    env_antes = dict(os.environ)

    carregar_env(tmp_path / "inexistente.env")

    # Nenhuma variavel nova foi adicionada
    assert os.environ == env_antes


def test_carregar_env_ignora_comentarios(tmp_path, monkeypatch):
    """Linhas com # devem ser ignoradas."""
    env_file = tmp_path / ".env"
    env_file.write_text(
        "# Este e um comentario\n"
        "  # Comentario com espaco\n"
        "DATABASE_URL=postgresql://ok@localhost/db\n",
        encoding="utf-8",
    )
    monkeypatch.delenv("DATABASE_URL", raising=False)

    carregar_env(env_file)

    assert os.environ["DATABASE_URL"] == "postgresql://ok@localhost/db"


def test_carregar_env_valor_com_aspas(tmp_path, monkeypatch):
    """Valores entre aspas devem ter as aspas removidas."""
    env_file = tmp_path / ".env"
    env_file.write_text(
        'DATABASE_URL="postgresql://quoted@localhost/db"\n',
        encoding="utf-8",
    )
    monkeypatch.delenv("DATABASE_URL", raising=False)

    carregar_env(env_file)

    assert os.environ["DATABASE_URL"] == "postgresql://quoted@localhost/db"
