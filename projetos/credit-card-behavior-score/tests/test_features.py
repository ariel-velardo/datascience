import numpy as np
import pandas as pd
import pytest
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline

from src.behavior_score.config import (
    FEATURES_FINAIS_ORIGINAIS,
    FEATURES_REMOVIDAS,
    VARIAVEIS_CATEGORICAS_FINAIS,
    VARIAVEIS_MODELO_FINAL,
    VARIAVEIS_NUMERICAS_FINAIS,
)
from src.behavior_score.features import (
    ConversorCategoricoTexto,
    ExtratorVar12Continua,
    IndicadoresEspeciaisVar12,
    criar_var12_estado,
    preparar_features_catboost,
)


def test_conversor_categorico_texto_preserva_codigos_e_missing() -> None:
    dados = pd.DataFrame({"categoria": [1.0, np.nan, 2.0]})
    resultado = ConversorCategoricoTexto().fit_transform(dados).ravel()
    assert resultado.tolist() == ["1.0", "__MISSING__", "2.0"]


def test_var12_continua_mascara_somente_codigos_especiais() -> None:
    dados = pd.DataFrame({"var12": [1.5, 99997, 99998, 99999, np.nan]})
    resultado = ExtratorVar12Continua().fit_transform(dados).ravel()
    assert resultado[0] == 1.5
    assert np.isnan(resultado[1:]).all()


def test_indicadores_var12_sao_exclusivos() -> None:
    dados = pd.DataFrame({"var12": [10, 99997, 99998, 99999]})
    resultado = IndicadoresEspeciaisVar12().fit_transform(dados)
    assert resultado.tolist() == [[0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1]]


def test_mediana_de_var12_ignora_os_codigos_especiais() -> None:
    """A mediana aprendida deve vir apenas do grupo regular de ``var12``.

    A ordem correta do pipeline é ``ExtratorVar12Continua`` -> ``SimpleImputer``.
    Se a ordem for invertida no futuro, os códigos especiais dominam a amostra
    (93% dos registros na base real) e a mediana aprendida deixa de representar
    a componente contínua. Este teste falha nesse cenário.
    """

    dados = pd.DataFrame(
        {"var12": [1.0, 2.0, 3.0, 99997.0, 99998.0, 99999.0, 99999.0, np.nan]}
    )
    pipeline = Pipeline(
        [
            ("extrator", ExtratorVar12Continua()),
            ("imputador", SimpleImputer(strategy="median")),
        ]
    )
    resultado = pipeline.fit_transform(dados).ravel()

    mediana_aprendida = pipeline.named_steps["imputador"].statistics_[0]
    assert mediana_aprendida == pytest.approx(2.0)
    assert resultado.tolist() == [1.0, 2.0, 3.0, 2.0, 2.0, 2.0, 2.0, 2.0]

    # Sem o extrator, a mediana seria dominada pelos códigos especiais.
    mediana_sem_extrator = (
        SimpleImputer(strategy="median").fit(dados).statistics_[0]
    )
    assert mediana_sem_extrator > 90000


def test_preparacao_catboost_preserva_flags_e_missing_categorico() -> None:
    dados = pd.DataFrame({"var12": [99997, 2.0], "cat_var2": [np.nan, 1.0]})
    resultado = preparar_features_catboost(dados, ["var12"], ["cat_var2"])
    assert np.isnan(resultado.loc[0, "var12"])
    assert resultado.loc[0, "var12_codigo_99997"] == 1
    assert resultado.loc[0, "cat_var2"] == "__MISSING__"


def test_criar_var12_estado_cobre_especiais_regular_e_missing() -> None:
    serie = pd.Series([99997, 99998, 99999, 42.5, np.nan])

    resultado = criar_var12_estado(serie)

    assert resultado.tolist() == [
        "99997",
        "99998",
        "99999",
        "REGULAR",
        "MISSING",
    ]
    assert resultado.name == "var12_estado"
    assert str(resultado.dtype) == "string"


def test_configuracao_final_exclui_features_removidas() -> None:
    assert FEATURES_FINAIS_ORIGINAIS == [
        "var1",
        "var3",
        "var4",
        "var5",
        "var7",
        "var8",
        "var9",
        "var11",
        "var12",
        "var14",
        "cat_var2",
        "cat_var10",
        "cat_var15",
    ]
    assert FEATURES_REMOVIDAS == ["cat_var6", "cat_var13"]
    assert VARIAVEIS_NUMERICAS_FINAIS == [
        "var1",
        "var3",
        "var4",
        "var5",
        "var7",
        "var8",
        "var9",
        "var11",
        "var14",
    ]
    assert VARIAVEIS_CATEGORICAS_FINAIS == [
        "cat_var2",
        "cat_var10",
        "cat_var15",
    ]
    assert VARIAVEIS_MODELO_FINAL == [
        *VARIAVEIS_NUMERICAS_FINAIS,
        *VARIAVEIS_CATEGORICAS_FINAIS,
        "var12_estado",
    ]
    assert set(FEATURES_REMOVIDAS).isdisjoint(FEATURES_FINAIS_ORIGINAIS)
    assert set(FEATURES_REMOVIDAS).isdisjoint(VARIAVEIS_MODELO_FINAL)
