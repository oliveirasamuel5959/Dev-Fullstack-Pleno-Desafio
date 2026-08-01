"""Motor de calculo de OEE — funcoes puras (sem dependencia de banco).

Fonte das formulas: docs/ESPECIFICACAO_TECNICA.md secao 4.

OEE = Disponibilidade x Performance x Qualidade  (produto, nunca media)

Disponibilidade = Tempo Rodando / Tempo Planejado de Producao
Performance     = (Tempo de Ciclo Ideal x Total Produzido) / Tempo Rodando
Qualidade       = Pecas Boas / Total Produzido

Todos os fatores sao clampados em [0, 1]. Dados inconsistentes geram
warning no stderr, nunca sao absorvidos silenciosamente.
"""

import sys


def _clamp(valor: float, minimo: float = 0.0, maximo: float = 1.0) -> float:
    """Clampa valor no intervalo [minimo, maximo]."""
    return max(minimo, min(maximo, valor))


def disponibilidade(tempo_rodando_s: float, tempo_planejado_s: float) -> float:
    """Calcula Disponibilidade = Tempo Rodando / Tempo Planejado.

    Args:
        tempo_rodando_s: Tempo em segundos que a maquina ficou rodando.
        tempo_planejado_s: Tempo em segundos planejado para producao
            (duracao do turno - paradas planejadas).

    Returns:
        Disponibilidade em [0, 1]. Retorna 0.0 se tempo_planejado_s == 0.
    """
    if tempo_planejado_s <= 0:
        return 0.0

    resultado = tempo_rodando_s / tempo_planejado_s

    if resultado > 1.0:
        print(
            f"[OEE] Disponibilidade {resultado:.4f} > 1.0 clampado — "
            f"tempo_rodando={tempo_rodando_s}s > "
            f"tempo_planejado={tempo_planejado_s}s?",
            file=sys.stderr,
        )
    elif resultado < 0.0:
        print(
            f"[OEE] Disponibilidade {resultado:.4f} < 0.0 clampado — "
            f"tempo_rodando={tempo_rodando_s}s negativo?",
            file=sys.stderr,
        )

    return _clamp(resultado)


def performance(
    ciclo_ideal_s: float,
    total_produzido: int,
    tempo_rodando_s: float,
) -> float:
    """Calcula Performance = (Ciclo Ideal x Total Produzido) / Tempo Rodando.

    Performance > 1.0 (100%) e capada em 1.0 — significa que a maquina
    produziu mais rapido que o ciclo ideal teorico (ciclo subestimado?).

    Args:
        ciclo_ideal_s: Tempo de ciclo ideal da maquina em segundos.
        total_produzido: Total de unidades produzidas no periodo.
        tempo_rodando_s: Tempo em segundos que a maquina ficou rodando.

    Returns:
        Performance em [0, 1]. Retorna 0.0 se tempo_rodando_s == 0.
    """
    if tempo_rodando_s <= 0:
        return 0.0

    tempo_ideal_total = ciclo_ideal_s * total_produzido
    resultado = tempo_ideal_total / tempo_rodando_s

    if resultado > 1.0:
        print(
            f"[OEE] Performance {resultado:.4f} > 1.0 clampado — "
            f"ciclo ideal subestimado? "
            f"ciclo_ideal={ciclo_ideal_s}s, "
            f"produzido={total_produzido}, "
            f"tempo_rodando={tempo_rodando_s}s",
            file=sys.stderr,
        )

    return _clamp(resultado)


def qualidade(produzidas: int, refugo: int) -> float:
    """Calcula Qualidade = Pecas Boas / Total Produzido.

    Args:
        produzidas: Total de unidades produzidas.
        refugo: Total de unidades com defeito (refugo).

    Returns:
        Qualidade em [0, 1]. Retorna 1.0 se produzidas == 0 (sem producao
        = sem refugo = qualidade perfeita por definicao).
    """
    if produzidas <= 0:
        return 1.0

    pecas_boas = produzidas - refugo
    resultado = pecas_boas / produzidas

    if resultado < 0.0:
        print(
            f"[OEE] Qualidade {resultado:.4f} < 0.0 clampado — "
            f"refugo={refugo} > produzidas={produzidas}?",
            file=sys.stderr,
        )

    return _clamp(resultado)


def oee(d: float, p: float, q: float) -> float:
    """Calcula OEE = Disponibilidade x Performance x Qualidade.

    OEE e o PRODUTO dos tres fatores, nunca a media.
    Cada fator deve ser previamente clampado em [0, 1].

    Args:
        d: Disponibilidade [0, 1].
        p: Performance [0, 1].
        q: Qualidade [0, 1].

    Returns:
        OEE em [0, 1].
    """
    return d * p * q
