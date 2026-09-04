"""Transformação da probabilidade de evento em Behavior Score."""

from __future__ import annotations

import numpy as np
from numpy.typing import ArrayLike


def calcular_behavior_score(
    probabilidade_evento: float | ArrayLike,
    base_score: float,
    pdo: float,
    base_odds: float,
    *,
    aplicar_clipping: bool = True,
) -> float | np.ndarray:
    """Converte probabilidades do evento adverso para a escala de score.

    A convenção utiliza odds de não-evento:evento, ``(1 - p) / p``. Assim,
    probabilidades maiores do evento produzem scores menores. ``base_score`` é
    atingido quando as odds são iguais a ``base_odds``; dobrar essas odds eleva
    o score em ``pdo`` pontos.

    Os parâmetros ``base_score``, ``pdo`` e ``base_odds`` definem a escala e
    devem ser fornecidos pelo chamador: esta função não os escolhe nem os
    calibra. Probabilidades iguais a zero ou um são protegidas por epsilon. Por
    padrão, o resultado é limitado ao intervalo operacional de 0 a 1000.

    Args:
        probabilidade_evento: Probabilidade escalar ou estrutura array-like.
        base_score: Score correspondente às odds de referência.
        pdo: Pontos acrescentados quando as odds de não-evento:evento dobram.
        base_odds: Odds de não-evento:evento associadas ao score base.
        aplicar_clipping: Se ``True``, limita o resultado ao intervalo [0, 1000].

    Returns:
        ``float`` para entrada escalar ou ``numpy.ndarray`` para array-like.

    Raises:
        ValueError: Se houver probabilidade fora de [0, 1], valor não finito ou
            parâmetro de escala inválido.
    """

    try:
        probabilidades = np.asarray(probabilidade_evento, dtype=float)
    except (TypeError, ValueError) as erro:
        raise ValueError("probabilidade_evento deve conter valores numéricos.") from erro

    entrada_escalar = probabilidades.ndim == 0
    if not np.all(np.isfinite(probabilidades)):
        raise ValueError("probabilidade_evento deve conter apenas valores finitos.")
    if np.any((probabilidades < 0.0) | (probabilidades > 1.0)):
        raise ValueError("probabilidade_evento deve estar no intervalo [0, 1].")

    parametros = {
        "base_score": base_score,
        "pdo": pdo,
        "base_odds": base_odds,
    }
    parametros_validados: dict[str, float] = {}
    for nome, valor in parametros.items():
        try:
            valor_numerico = float(valor)
        except (TypeError, ValueError, OverflowError) as erro:
            raise ValueError(f"{nome} deve ser um número finito.") from erro
        if not np.isfinite(valor_numerico):
            raise ValueError(f"{nome} deve ser um número finito.")
        parametros_validados[nome] = valor_numerico

    base_score_validado = parametros_validados["base_score"]
    pdo_validado = parametros_validados["pdo"]
    base_odds_validado = parametros_validados["base_odds"]
    if pdo_validado <= 0.0:
        raise ValueError("pdo deve ser maior que zero.")
    if base_odds_validado <= 0.0:
        raise ValueError("base_odds deve ser maior que zero.")

    epsilon = np.finfo(float).eps
    probabilidades_protegidas = np.clip(
        probabilidades,
        epsilon,
        1.0 - epsilon,
    )
    odds_nao_evento_evento = (
        1.0 - probabilidades_protegidas
    ) / probabilidades_protegidas
    fator = pdo_validado / np.log(2.0)
    score = base_score_validado + fator * (
        np.log(odds_nao_evento_evento) - np.log(base_odds_validado)
    )

    if aplicar_clipping:
        score = np.clip(score, 0.0, 1000.0)

    if entrada_escalar:
        return float(score)
    return np.asarray(score, dtype=float)
