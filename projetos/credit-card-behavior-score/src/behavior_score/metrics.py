"""Métricas de discriminação e calibração do Behavior Score."""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    roc_auc_score,
    roc_curve,
)


def _validar_alvo_binario(y_verdadeiro: object) -> np.ndarray:
    alvo = np.asarray(y_verdadeiro)
    if set(np.unique(alvo)) != {0, 1}:
        raise ValueError("A métrica exige alvo binário contendo as classes 0 e 1.")
    return alvo


def calcular_gini(y_verdadeiro: object, probabilidade: object) -> float:
    """Calcula Gini como ``2 * ROC-AUC - 1``."""

    alvo = _validar_alvo_binario(y_verdadeiro)
    return float(2 * roc_auc_score(alvo, probabilidade) - 1)


def calcular_ks(y_verdadeiro: object, probabilidade: object) -> float:
    """Calcula a distância máxima entre as distribuições acumuladas das classes."""

    alvo = _validar_alvo_binario(y_verdadeiro)
    taxa_falso_positivo, taxa_verdadeiro_positivo, _ = roc_curve(
        alvo, probabilidade
    )
    return float(np.max(np.abs(taxa_verdadeiro_positivo - taxa_falso_positivo)))


def calcular_metricas_classificacao(
    y_verdadeiro: object,
    probabilidade: object,
) -> dict[str, float]:
    """Calcula métricas principais sem escolher threshold de classificação."""

    alvo = _validar_alvo_binario(y_verdadeiro)
    probabilidade = np.asarray(probabilidade, dtype=float)
    return {
        "roc_auc": float(roc_auc_score(alvo, probabilidade)),
        "gini": calcular_gini(alvo, probabilidade),
        "ks": calcular_ks(alvo, probabilidade),
        "pr_auc": float(average_precision_score(alvo, probabilidade)),
        "brier": float(brier_score_loss(alvo, probabilidade)),
    }


def calcular_lift_por_decil(
    y_verdadeiro: object,
    probabilidade: object,
    quantidade_faixas: int = 10,
) -> pd.DataFrame:
    """Resume evento, lift e captura acumulada por faixas ordenadas de risco."""

    alvo = _validar_alvo_binario(y_verdadeiro)
    probabilidades = np.asarray(probabilidade, dtype=float)
    if len(alvo) != len(probabilidades):
        raise ValueError("Alvo e probabilidade devem possuir o mesmo tamanho.")

    tabela = pd.DataFrame({"alvo": alvo, "probabilidade": probabilidades})
    ordem = tabela["probabilidade"].rank(method="first", ascending=False)
    tabela["decil"] = pd.qcut(
        ordem,
        q=min(quantidade_faixas, len(tabela)),
        labels=False,
    ) + 1
    resumo = (
        tabela.groupby("decil", as_index=False)
        .agg(
            quantidade=("alvo", "size"),
            eventos=("alvo", "sum"),
            taxa_evento=("alvo", "mean"),
            probabilidade_media=("probabilidade", "mean"),
        )
        .sort_values("decil")
    )
    taxa_global = tabela["alvo"].mean()
    resumo["lift"] = resumo["taxa_evento"] / taxa_global
    resumo["captura_acumulada"] = resumo["eventos"].cumsum() / tabela["alvo"].sum()
    return resumo
