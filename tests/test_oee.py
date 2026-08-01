"""Testes do motor de OEE — funcoes puras e golden self-check.

Golden case: docs/CONTEXTO_NEGOCIO.md secao 2.
Turno 8h (480min), 60min paradas, ciclo 0.5s, 480.000 produzidas, 24.000 refugo.

D = 420/480 = 0.875
Q = (480.000 - 24.000) / 480.000 = 0.95

Nota: O documento calcula P = 240.000/25.200 ≈ 0.952, mas 240.000/25.200 = 9.52.
O proprio documento anota "limitado a 100% na pratica; ajuste ciclo ideal",
reconhecendo que o valor e >1.0 e deve ser clampado. O calculo final de OEE
usa P ≈ 0.95 conforme a linha:
  OEE ≈ 0.875 x 0.95 x 0.95 ≈ 0.79 (79%)

Portanto, o golden case testa:
- D = 0.875 (exato)
- Q = 0.95 (exato)
- P com os numeros do documento = 9.52 → clamp 1.0 (comportamento correto)
- OEE com P=0.95 (valor do documento) = 0.875 x 0.95 x 0.95 ≈ 0.79
"""

import math

from oee_textil.services.oee import disponibilidade, oee, performance, qualidade

# Constantes do golden case
GOLDEN_TEMPO_PLANEJADO_S = 480 * 60  # 8h = 28800s
GOLDEN_TEMPO_RODANDO_S = 420 * 60  # 7h = 25200s
GOLDEN_CICLO_IDEAL_S = 0.5
GOLDEN_TOTAL_PRODUZIDO = 480_000
GOLDEN_REFUGO = 24_000


# ---------------------------------------------------------------------------
# Golden case — formulas individuais
# ---------------------------------------------------------------------------


def test_golden_disponibilidade():
    """D = 420/480 = 0.875."""
    d = disponibilidade(GOLDEN_TEMPO_RODANDO_S, GOLDEN_TEMPO_PLANEJADO_S)
    assert math.isclose(d, 0.875, rel_tol=1e-6)


def test_golden_performance_com_clamp():
    """P = (0.5 x 480000) / 25200 = 9.52 → clamp 1.0.

    O documento do CONTEXTO_NEGOCIO.md calcula 240.000/25.200 ≈ 0.952,
    mas a conta correta e 9.52. O proprio documento reconhece:
    "limitado a 100% na pratica; ajuste ciclo ideal".

    O comportamento correto da funcao e clampar em 1.0.
    """
    p = performance(
        GOLDEN_CICLO_IDEAL_S, GOLDEN_TOTAL_PRODUZIDO, GOLDEN_TEMPO_RODANDO_S
    )
    # Com os numeros do documento, P bruta = 9.52 → clamp 1.0
    assert p == 1.0, f"P={p} deveria ser clampada para 1.0"


def test_golden_performance_valor_documento():
    """P com os valores semanticos do documento: P ≈ 0.95.

    O documento usa P = 0.95 no calculo final:
    OEE ≈ 0.875 x 0.95 x 0.95 ≈ 0.79

    Para obter P = 0.95 com a formula, basta fornecer os numeros corretos.
    Aqui testamos que a funcao retorna o valor esperado quando alimentada
    com dados que produzem P ≈ 0.95.
    """
    # P = 0.95 = (ciclo x total) / tempo_rodando
    # Com ciclo=0.5, tempo_rodando=25200:
    # total = 0.95 x 25200 / 0.5 = 47880
    p = performance(0.5, 47880, 25200)
    assert math.isclose(p, 0.95, rel_tol=1e-6)


def test_golden_qualidade():
    """Q = (480000 - 24000) / 480000 = 0.95."""
    q = qualidade(GOLDEN_TOTAL_PRODUZIDO, GOLDEN_REFUGO)
    assert math.isclose(q, 0.95, rel_tol=1e-6)


def test_golden_oee():
    """OEE = 0.875 x 0.95 x 0.95 ≈ 0.79 (conforme o documento).

    Nota: O documento diz "OEE ≈ 0,875 x 0,95 x 0,95 ≈ 0,79 (79%)".
    Usamos P=0.95 como stated no calculo final do documento.
    """
    d = disponibilidade(GOLDEN_TEMPO_RODANDO_S, GOLDEN_TEMPO_PLANEJADO_S)
    q = qualidade(GOLDEN_TOTAL_PRODUZIDO, GOLDEN_REFUGO)

    # D = 0.875, Q = 0.95
    assert math.isclose(d, 0.875, rel_tol=1e-6)
    assert math.isclose(q, 0.95, rel_tol=1e-6)

    # OEE com P=0.95 (valor do documento)
    resultado = oee(d, 0.95, q)

    # OEE ≈ 0.79 (tolerancia de 0.02)
    assert 0.78 <= resultado <= 0.80, f"OEE esperado ≈ 0.79, obtido {resultado}"


# ---------------------------------------------------------------------------
# Clamp
# ---------------------------------------------------------------------------


def test_disponibilidade_clamp_superior():
    """D > 1.0 deve ser clampado para 1.0."""
    assert disponibilidade(100, 80) == 1.0


def test_disponibilidade_clamp_inferior():
    """D < 0.0 deve ser clampado para 0.0."""
    assert disponibilidade(-10, 100) == 0.0


def test_performance_clamp_superior():
    """P > 1.0 deve ser clampado para 1.0 (cap at 100%)."""
    # Ciclo ideal superestimado → P > 1.0
    p = performance(1.0, 1000, 500)
    assert p == 1.0


def test_qualidade_clamp_inferior():
    """Q < 0.0 (refugo > produzidas) deve ser clampado para 0.0."""
    q = qualidade(100, 200)
    assert q == 0.0


# ---------------------------------------------------------------------------
# Divisao por zero / edge cases
# ---------------------------------------------------------------------------


def test_disponibilidade_zero_planejado():
    """Tempo planejado == 0 → D = 0.0."""
    assert disponibilidade(0, 0) == 0.0


def test_performance_zero_rodando():
    """Tempo rodando == 0 → P = 0.0."""
    assert performance(0.5, 1000, 0) == 0.0


def test_qualidade_zero_produzidas():
    """Produzidas == 0 → Q = 1.0 (sem producao = sem refugo)."""
    assert qualidade(0, 0) == 1.0


def test_disponibilidade_perfeita():
    """Tempo rodando == tempo planejado → D = 1.0."""
    assert disponibilidade(100, 100) == 1.0


def test_performance_perfeita():
    """Ciclo ideal x produzido == tempo rodando → P = 1.0."""
    p = performance(1.0, 100, 100)
    assert p == 1.0


def test_qualidade_perfeita():
    """Zero refugo → Q = 1.0."""
    assert qualidade(100, 0) == 1.0


def test_oee_perfeito():
    """D=P=Q=1.0 → OEE = 1.0."""
    assert oee(1.0, 1.0, 1.0) == 1.0


def test_oee_zero():
    """Qualquer fator = 0 → OEE = 0."""
    assert oee(0.0, 1.0, 1.0) == 0.0
    assert oee(1.0, 0.0, 1.0) == 0.0
    assert oee(1.0, 1.0, 0.0) == 0.0


# ---------------------------------------------------------------------------
# OEE e produto, nao media
# ---------------------------------------------------------------------------


def test_oee_produto_nao_media():
    """OEE = D x P x Q, diferente de (D+P+Q)/3."""
    d, p, q = 0.8, 0.9, 0.7
    produto = oee(d, p, q)
    media = (d + p + q) / 3
    assert produto != media, f"OEE={produto} nao deve ser igual a media={media}"
    assert math.isclose(produto, 0.504, rel_tol=1e-6)


def test_oee_media_seria_errado():
    """O exemplo do README.md §4: a media (0.875+0.952+0.95)/3 ≈ 0.926
    nao e o valor correto. O produto ≈ 0.79 e o correto.
    """
    d, p, q = 0.875, 0.9523809, 0.95
    media = (d + p + q) / 3
    produto = oee(d, p, q)

    # A media seria ~0.926, o produto ~0.791
    assert media > 0.92, f"Media esperada ~0.926, obtida {media}"
    assert produto < 0.81, f"Produto esperado ~0.791, obtido {produto}"
    assert media != produto
