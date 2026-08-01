"""Configuracao da aplicacao — leitura de variaveis de ambiente.

Carrega .env da raiz do repositorio (formato KEY=VALUE, ignora # e linhas
vazias) sem sobrescrever variaveis ja definidas no ambiente. Sem dependencia
de pydantic-settings ou python-dotenv — ~15 linhas de Python puro.

Uso:
    from oee_textil.core.config import get_database_url
    url = get_database_url()
"""

import os
from pathlib import Path

DEFAULT_DATABASE_URL = "postgresql://oee:oee_dev@localhost:5432/oee_textil"


def _repo_root() -> Path:
    """Retorna a raiz do repositorio (3 niveis acima deste arquivo)."""
    return Path(__file__).resolve().parents[3]


def carregar_env(arquivo: Path | None = None) -> None:
    """Le .env (KEY=VALUE) e popula os.environ sem sobrescrever vars existentes.

    Args:
        arquivo: Caminho explicito para o .env. Se None, procura em:
                 1. Path.cwd() / ".env"
                 2. _repo_root() / ".env"
    """
    if arquivo is None:
        cwd_env = Path.cwd() / ".env"
        repo_env = _repo_root() / ".env"
        if cwd_env.exists():
            arquivo = cwd_env
        elif repo_env.exists():
            arquivo = repo_env
        else:
            return  # nenhum .env encontrado, silencioso

    if not arquivo.exists():
        return

    with open(arquivo, encoding="utf-8") as f:
        for linha in f:
            stripped = linha.strip()
            # Ignorar comentarios e linhas vazias
            if not stripped or stripped.startswith("#"):
                continue
            if "=" not in stripped:
                continue
            chave, _, valor = stripped.partition("=")
            chave = chave.strip()
            valor = valor.strip().strip('"').strip("'")
            # Nao sobrescrever variaveis ja definidas no ambiente
            if chave not in os.environ:
                os.environ[chave] = valor


def get_database_url() -> str:
    """Retorna a URL de conexao com o banco de dados.

    Prioridade:
    1. Variavel de ambiente DATABASE_URL
    2. Fallback para o default de desenvolvimento local (docker compose)
    """
    return os.environ.get("DATABASE_URL", DEFAULT_DATABASE_URL)


# Carregar .env no import do modulo (side effect documentado).
# Avaliado uma vez; seguro para testes porque nao sobrescreve vars existentes.
carregar_env()
