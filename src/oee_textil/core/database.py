"""Engine e sessao SQLAlchemy — ponto central de acesso ao banco de dados.

Fornece a Base declarativa, o engine e a fabrica de sessoes (SessionLocal).
Importar este modulo NAO conecta ao banco (create_engine e lazy).

Uso:
    from oee_textil.core.database import Base, engine, SessionLocal
    session = SessionLocal()
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from oee_textil.core.config import get_database_url


class Base(DeclarativeBase):
    """Base declarativa unica de todos os modelos ORM do projeto."""


engine = create_engine(
    get_database_url(),
    pool_pre_ping=True,  # verifica conexao antes de usar (banco em container)
)

SessionLocal = sessionmaker(
    bind=engine,
    expire_on_commit=False,  # evita re-query apos commit (padrao de ingestao)
    autoflush=False,  # controle explicito de flush
)
