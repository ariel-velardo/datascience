import numpy as np
import pandas as pd
import pytest

from src.behavior_score.stability import (
    ROTULO_MISSING,
    calcular_limites_referencia,
    calcular_psi,
    calcular_psi_categorico,
    calcular_psi_numerico,
)


def test_psi_numerico_de_distribuicoes_identicas_e_proximo_de_zero() -> None:
    valores = np.linspace(0, 100, 1000)
    assert calcular_psi_numerico(valores, valores) == pytest.approx(0.0, abs=1e-9)


def test_psi_categorico_de_distribuicoes_identicas_e_proximo_de_zero() -> None:
    categorias = ["a"] * 60 + ["b"] * 30 + ["c"] * 10
    assert calcular_psi_categorico(categorias, categorias) == pytest.approx(0.0, abs=1e-9)


def test_psi_numerico_cresce_com_o_deslocamento() -> None:
    referencia = np.linspace(0, 100, 1000)
    psi_pequeno = calcular_psi_numerico(referencia, referencia + 5)
    psi_grande = calcular_psi_numerico(referencia, referencia + 40)
    assert 0 < psi_pequeno < psi_grande


def test_psi_categorico_detecta_inversao_de_participacao() -> None:
    referencia = ["a"] * 90 + ["b"] * 10
    comparacao = ["a"] * 10 + ["b"] * 90
    assert calcular_psi_categorico(referencia, comparacao) > 1.0


def test_limites_vem_apenas_da_referencia() -> None:
    referencia = np.arange(100.0)
    limites = calcular_limites_referencia(referencia)
    assert limites is not None
    assert limites[0] == -np.inf and limites[-1] == np.inf
    assert len(limites) == 11
    # Valores muito fora do intervalo da referência não criam faixas novas:
    # eles caem nas faixas extremas, que são abertas.
    fora = np.array([-1e9, 1e9])
    assert np.isfinite(calcular_psi_numerico(referencia, fora))


def test_referencia_sem_variacao_retorna_nan() -> None:
    constante = np.ones(50)
    assert np.isnan(calcular_psi_numerico(constante, np.arange(50.0)))


def test_missing_forma_categoria_propria_e_altera_o_psi() -> None:
    referencia = pd.Series(["a"] * 50 + ["b"] * 50)
    sem_missing = pd.Series(["a"] * 50 + ["b"] * 50)
    com_missing = pd.Series(["a"] * 50 + [None] * 50)
    assert calcular_psi_categorico(referencia, sem_missing) == pytest.approx(0.0, abs=1e-9)
    assert calcular_psi_categorico(referencia, com_missing) > 1.0

    referencia_numerica = pd.Series(np.linspace(0, 10, 100))
    com_nan = referencia_numerica.mask(referencia_numerica > 5)
    assert calcular_psi_numerico(referencia_numerica, com_nan) > 0.0


def test_missing_numerico_nao_entra_no_calculo_dos_quantis() -> None:
    completa = pd.Series(np.arange(100.0))
    com_missing = completa.mask(completa >= 50)
    assert np.array_equal(
        calcular_limites_referencia(completa.head(50)),
        calcular_limites_referencia(com_missing),
    )


def test_categoria_nova_gera_psi_positivo_e_finito() -> None:
    referencia = ["a"] * 80 + ["b"] * 20
    comparacao = ["a"] * 78 + ["b"] * 20 + ["nova"] * 2
    psi = calcular_psi_categorico(referencia, comparacao)
    assert np.isfinite(psi)
    assert psi > 0.1


def test_epsilon_controla_a_penalidade_de_categoria_nova() -> None:
    referencia = ["a"] * 80 + ["b"] * 20
    comparacao = ["a"] * 78 + ["b"] * 20 + ["nova"] * 2
    psi_epsilon_menor = calcular_psi_categorico(referencia, comparacao, epsilon=1e-9)
    psi_epsilon_maior = calcular_psi_categorico(referencia, comparacao, epsilon=1e-3)
    # Piso menor implica log(q / p) maior: a categoria nova pesa mais.
    assert psi_epsilon_menor > psi_epsilon_maior
    assert np.isfinite(psi_epsilon_menor)


def test_valores_especiais_formam_categorias_proprias() -> None:
    regulares = list(np.arange(100.0))
    referencia = pd.Series(regulares + [99999.0] * 100)
    comparacao = pd.Series(regulares + [99999.0] * 10)

    # Declarado como especial, o código não desloca os quantis da parte regular.
    limites = calcular_limites_referencia(referencia, especiais=(99999,))
    assert limites is not None
    assert np.isfinite(limites[1:-1]).all()
    assert limites[1:-1].max() < 100.0

    # Sem declarar, os cortes internos passam a ser dominados pelo código.
    limites_contaminados = calcular_limites_referencia(referencia)
    assert limites_contaminados is not None
    assert limites_contaminados[1:-1].max() > 100.0

    # A mudança de frequência do código especial é capturada pelo PSI.
    assert calcular_psi_numerico(referencia, comparacao, especiais=(99999,)) > 0.5


def test_rotulo_missing_e_o_documentado() -> None:
    assert ROTULO_MISSING == "__MISSING__"


def test_despachante_rejeita_tipo_invalido() -> None:
    with pytest.raises(ValueError, match="numerica"):
        calcular_psi([1, 2, 3], [1, 2, 3], tipo="outro")
