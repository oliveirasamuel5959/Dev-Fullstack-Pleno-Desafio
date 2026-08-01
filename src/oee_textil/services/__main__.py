"""Permite executar o consumidor via python -m oee_textil.services.consumidor.

Nota: este __main__.py permite `python -m oee_textil.services`,
mas o entry point canonico do consumidor e `python -m oee_textil.services.consumidor`
(que e o que o Dockerfile usa). Ambos funcionam.
"""

import asyncio

from oee_textil.services.consumidor import main

asyncio.run(main())
