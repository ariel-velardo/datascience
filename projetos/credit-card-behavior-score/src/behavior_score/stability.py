"""Métricas de estabilidade populacional do Behavior Score.

Implementação única de PSI (*Population Stability Index*) do projeto. Antes desta
consolidação existiam duas versões divergentes escritas dentro de notebooks.

Convenções adotadas e mantidas explicitamente:

- os limites das faixas numéricas são definidos **exclusivamente** pela amostra de
  referência; a amostra comparada nunca redefine os cortes;
- valores ausentes formam uma categoria própria (``__MISSING__``) em vez de serem
  descartados;
- valores especiais informados formam uma categoria própria cada, e são removidos
  do cálculo dos quantis da referência;
- proporções nulas recebem um piso ``epsilon`` para evitar divisão por zero e
  logaritmo de zero. O piso **não** é renormalizado: uma categoria presente apenas
  na amostra comparada gera contribuição elevada e proporcional a
  ``log(q / epsilon)``. Esse comportamento é intencional e coberto por testes.

O PSI é utilizado como ferramenta diagnóstica e não como regra automática de
exclusão de variáveis.
"""

from __future__ import annotations

from collections.abc import Iterable

import numpy as np
import pandas as pd


ROTULO_MISSING = "__MISSING__"
EPSILON_PADRAO = 1e-6
QUANTIDADE_FAIXAS_PADRAO = 10


def _contribuicao_psi(
    proporcao_referencia: pd.Series,
    proporcao_comparacao: pd.Series,
    epsilon: float,
) -> float:
    """Soma ``(q - p) * log(q / p)`` com piso ``epsilon`` nas proporções."""

    p = proporcao_referencia.clip(lower=epsilon)
    q = proporcao_comparacao.clip(lower=epsilon)
    return float(((q - p) * np.log(q / p)).sum())


def _alinhar_categorias(
    referencia: pd.Series,
    comparacao: pd.Series,
) -> tuple[pd.Series, pd.Series]:
    """Alinha as duas distribuições sobre a união das categorias observadas."""

    categorias = referencia.unique().tolist()
    vistas = set(categorias)
    categorias += [c for c in comparacao.unique() if c not in vistas]

    proporcao_referencia = (
        referencia.value_counts(normalize=True).reindex(categorias, fill_value=0.0)
    )
    proporcao_comparacao = (
        comparacao.value_counts(normalize=True).reindex(categorias, fill_value=0.0)
    )
    return proporcao_referencia, proporcao_comparacao


def _rotular_categorico(valores: object) -> pd.Series:
    """Converte para texto e transforma ausência em categoria explícita."""

    return pd.Series(valores).astype("string").fillna(ROTULO_MISSING)


def calcular_limites_referencia(
    referencia: object,
    especiais: Iterable[float] = (),
    quantidade_faixas: int = QUANTIDADE_FAIXAS_PADRAO,
) -> np.ndarray | None:
    """Calcula os cortes de faixa a partir apenas da amostra de referência.

    Valores ausentes e valores especiais são excluídos do cálculo dos quantis.
    Os extremos são abertos para que a amostra comparada nunca caia fora das
    faixas nem redefina os cortes.

    Retorna ``None`` quando a referência não possui variação suficiente.
    """

    serie = pd.Series(referencia)
    codigos = set(especiais)
    regulares = serie[serie.notna() & ~serie.isin(codigos)]
    if regulares.empty:
        return None

    quantis = np.linspace(0, 1, quantidade_faixas + 1)
    limites = np.unique(regulares.quantile(quantis).to_numpy())
    if len(limites) < 2:
        return None

    limites = limites.astype(float)
    limites[0], limites[-1] = -np.inf, np.inf
    return limites


def _rotular_numerico(
    valores: object,
    limites: np.ndarray,
    especiais: Iterable[float],
) -> pd.Series:
    """Aplica os cortes da referência e isola ausência e valores especiais."""

    serie = pd.Series(valores)
    rotulos = (
        pd.cut(serie, limites, include_lowest=True)
        .astype("string")
        .fillna(ROTULO_MISSING)
    )
    for codigo in especiais:
        rotulos.loc[serie.eq(codigo)] = f"__ESPECIAL_{codigo}__"
    return rotulos


def calcular_psi_numerico(
    referencia: object,
    comparacao: object,
    especiais: Iterable[float] = (),
    quantidade_faixas: int = QUANTIDADE_FAIXAS_PADRAO,
    epsilon: float = EPSILON_PADRAO,
) -> float:
    """Calcula o PSI de uma variável numérica.

    Os limites das faixas vêm somente da referência. Ausência e cada valor
    especial informado formam categorias próprias.

    Retorna ``NaN`` quando a referência não permite construir faixas.
    """

    codigos = tuple(especiais)
    limites = calcular_limites_referencia(referencia, codigos, quantidade_faixas)
    if limites is None:
        return float("nan")

    rotulos_referencia = _rotular_numerico(referencia, limites, codigos)
    rotulos_comparacao = _rotular_numerico(comparacao, limites, codigos)
    proporcoes = _alinhar_categorias(rotulos_referencia, rotulos_comparacao)
    return _contribuicao_psi(*proporcoes, epsilon=epsilon)


def calcular_psi_categorico(
    referencia: object,
    comparacao: object,
    epsilon: float = EPSILON_PADRAO,
) -> float:
    """Calcula o PSI de uma variável categórica.

    Ausência forma a categoria ``__MISSING__``. Categorias presentes apenas na
    amostra comparada entram no cálculo com a proporção de referência no piso
    ``epsilon``.
    """

    rotulos_referencia = _rotular_categorico(referencia)
    rotulos_comparacao = _rotular_categorico(comparacao)
    proporcoes = _alinhar_categorias(rotulos_referencia, rotulos_comparacao)
    return _contribuicao_psi(*proporcoes, epsilon=epsilon)


def calcular_psi(
    referencia: object,
    comparacao: object,
    tipo: str,
    especiais: Iterable[float] = (),
    quantidade_faixas: int = QUANTIDADE_FAIXAS_PADRAO,
    epsilon: float = EPSILON_PADRAO,
) -> float:
    """Despacha o cálculo de PSI conforme ``tipo`` (``numerica`` ou ``categorica``)."""

    if tipo == "numerica":
        return calcular_psi_numerico(
            referencia,
            comparacao,
            especiais=especiais,
            quantidade_faixas=quantidade_faixas,
            epsilon=epsilon,
        )
    if tipo == "categorica":
        return calcular_psi_categorico(referencia, comparacao, epsilon=epsilon)
    raise ValueError("O parâmetro 'tipo' deve ser 'numerica' ou 'categorica'.")
