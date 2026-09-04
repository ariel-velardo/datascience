import numpy as np
import pytest

from src.behavior_score.scoring import calcular_behavior_score


def test_direcao_ponto_base_pdo_e_tipos_de_retorno() -> None:
    base_score, pdo, base_odds = 500.0, 40.0, 9.0
    probabilidade_base = 1.0 / (1.0 + base_odds)
    probabilidade_odds_dobradas = 1.0 / (1.0 + 2.0 * base_odds)

    score_base = calcular_behavior_score(
        probabilidade_base, base_score, pdo, base_odds, aplicar_clipping=False
    )
    scores = calcular_behavior_score(
        [probabilidade_odds_dobradas, probabilidade_base, 0.20],
        base_score,
        pdo,
        base_odds,
        aplicar_clipping=False,
    )

    assert isinstance(score_base, float)
    assert isinstance(scores, np.ndarray)
    assert score_base == pytest.approx(base_score)
    assert scores[0] == pytest.approx(base_score + pdo)
    assert scores[0] > scores[1] > scores[2]


def test_score_e_monotono_nao_crescente_e_estrito_no_miolo() -> None:
    probabilidades = np.array([0.0, 1e-12, 0.01, 0.10, 0.50, 0.90, 0.99, 1.0])
    scores = calcular_behavior_score(probabilidades, 500.0, 50.0, 1.0)

    assert np.all(np.diff(scores) <= 0.0)
    assert np.all(np.diff(scores[2:7]) < 0.0)


def test_clipping_respeita_limites_e_pode_ser_desativado() -> None:
    probabilidades = [0.0, 1.0]
    com_clipping = calcular_behavior_score(probabilidades, 500.0, 100.0, 1.0)
    sem_clipping = calcular_behavior_score(
        probabilidades, 500.0, 100.0, 1.0, aplicar_clipping=False
    )

    assert com_clipping.tolist() == [1000.0, 0.0]
    assert sem_clipping[0] > 1000.0
    assert sem_clipping[1] < 0.0


def test_extremos_e_probabilidades_proximas_sao_finitos_e_ordenados() -> None:
    probabilidades = [0.0, 1e-12, 0.5, 1.0 - 1e-12, 1.0]
    scores = calcular_behavior_score(
        probabilidades, 500.0, 50.0, 1.0, aplicar_clipping=False
    )

    assert np.isfinite(scores).all()
    assert np.all(np.diff(scores) < 0.0)


def test_transformacao_e_deterministica() -> None:
    probabilidades = np.array([0.02, 0.10, 0.35, 0.80])
    primeira = calcular_behavior_score(probabilidades, 600.0, 45.0, 20.0)
    segunda = calcular_behavior_score(probabilidades, 600.0, 45.0, 20.0)

    assert np.array_equal(primeira, segunda)


def test_rejeita_probabilidades_e_parametros_invalidos() -> None:
    for probabilidades in ([np.nan], [np.inf], [-0.01], [1.01]):
        with pytest.raises(ValueError, match="probabilidade_evento"):
            calcular_behavior_score(probabilidades, 500.0, 50.0, 10.0)

    parametros_invalidos = [
        (np.nan, 50.0, 10.0, "base_score"),
        (500.0, np.inf, 10.0, "pdo"),
        (500.0, 0.0, 10.0, "pdo"),
        (500.0, 50.0, np.nan, "base_odds"),
        (500.0, 50.0, 0.0, "base_odds"),
    ]
    for base_score, pdo, base_odds, nome in parametros_invalidos:
        with pytest.raises(ValueError, match=nome):
            calcular_behavior_score(0.10, base_score, pdo, base_odds)
