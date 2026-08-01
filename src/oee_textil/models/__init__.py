"""Models — modelos SQLAlchemy (ORM).

Mapeamento objeto-relacional das entidades de dominio: catalogo de maquinas,
hypertable de telemetria, eventos de estado/parada, producao, motivos e turnos.

Os imports abaixo registram todas as tabelas no Base.metadata para o Alembic.
"""

from oee_textil.models.estado import EstadoMaquina  # noqa: F401
from oee_textil.models.maquina import Maquina  # noqa: F401
from oee_textil.models.motivo_parada import MotivoParada  # noqa: F401
from oee_textil.models.parada import Parada  # noqa: F401
from oee_textil.models.producao import Producao  # noqa: F401
from oee_textil.models.telemetria import Telemetria  # noqa: F401
from oee_textil.models.turno import Turno  # noqa: F401
