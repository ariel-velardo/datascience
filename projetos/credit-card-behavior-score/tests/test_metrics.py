import numpy as np
import pytest

from src.behavior_score.metrics import (
    calcular_gini,
    calcular_ks,
    calcular_lift_por_decil,
    calcular_metricas_classificacao,
)


def test_gini_perfeito_e_invertido() -> None:
    alvo = np.array([0, 0, 1, 1])
    assert calcular_gini(alvo, [0.1, 0.2, 0.8, 0.9]) == pytest.approx(1.0)
    assert calcular_gini(alvo, [0.9, 0.8, 0.2, 0.1]) == pytest.approx(-1.0)


def test_ks_perfeito() -> None:
    assert calcular_ks([0, 0, 1, 1], [0.1, 0.2, 0.8, 0.9]) == pytest.approx(1.0)


def test_metricas_rejeitam_alvo_com_uma_classe() -> None:
    with pytest.raises(ValueError, match="classes 0 e 1"):
        calcular_metricas_classificacao([0, 0], [0.1, 0.2])


def test_lift_preserva_totais_e_ordem_de_risco() -> None:
    tabela = calcular_lift_por_decil(
        [0, 0, 0, 0, 1, 1, 1, 1, 1, 1],
        [0.01, 0.02, 0.03, 0.04, 0.5, 0.6, 0.7, 0.8, 0.9, 0.99],
        quantidade_faixas=5,
    )
    assert tabela["quantidade"].sum() == 10
    assert tabela["eventos"].sum() == 6
    assert tabela.iloc[0]["probabilidade_media"] > tabela.iloc[-1]["probabilidade_media"]
    assert tabela.iloc[-1]["captura_acumulada"] == pytest.approx(1.0)
