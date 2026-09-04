"""Transformações determinísticas de features do Behavior Score."""

from __future__ import annotations

from collections.abc import Iterable

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin


CODIGOS_ESPECIAIS_VAR12 = (99997, 99998, 99999)
ROTULO_VAR12_REGULAR = "REGULAR"
ROTULO_VAR12_MISSING = "MISSING"


def criar_var12_estado(serie_var12: pd.Series) -> pd.Series:
    """Representa ``var12`` pelos estados categóricos da especificação final.

    Os códigos especiais são preservados como texto, valores regulares recebem
    ``REGULAR`` e valores ausentes recebem ``MISSING``.
    """

    estado = pd.Series(
        ROTULO_VAR12_REGULAR,
        index=serie_var12.index,
        dtype="string",
        name="var12_estado",
    )
    for codigo in CODIGOS_ESPECIAIS_VAR12:
        mascara_codigo = serie_var12.eq(codigo).fillna(False)
        estado.loc[mascara_codigo] = str(codigo)
    estado.loc[serie_var12.isna()] = ROTULO_VAR12_MISSING
    return estado


class ConversorCategoricoTexto(BaseEstimator, TransformerMixin):
    """Converte códigos categóricos para texto e explicita valores ausentes."""

    def __init__(self, rotulo_missing: str = "__MISSING__") -> None:
        self.rotulo_missing = rotulo_missing

    def fit(self, X: object, y: object = None) -> "ConversorCategoricoTexto":
        """Registra os nomes de entrada; não aprende estatísticas."""

        quadro = pd.DataFrame(X)
        self.feature_names_in_ = np.asarray(quadro.columns.astype(str), dtype=object)
        return self

    def transform(self, X: object) -> np.ndarray:
        """Retorna matriz de strings compatível com OneHotEncoder."""

        quadro = pd.DataFrame(X).copy()
        for coluna in quadro.columns:
            serie = quadro[coluna]
            quadro[coluna] = serie.map(
                lambda valor: self.rotulo_missing if pd.isna(valor) else str(valor)
            )
        return quadro.to_numpy(dtype=object)

    def get_feature_names_out(self, input_features: object = None) -> np.ndarray:
        """Preserva os nomes das colunas categóricas."""

        if input_features is not None:
            return np.asarray(input_features, dtype=object)
        return self.feature_names_in_


class ExtratorVar12Continua(BaseEstimator, TransformerMixin):
    """Implementa a representação histórica contínua de ``var12``.

    Esta transformação foi usada no desenvolvimento, mas não corresponde à
    especificação final baseada em ``var12_estado``.
    """

    def __init__(
        self,
        codigos_especiais: Iterable[int] = CODIGOS_ESPECIAIS_VAR12,
    ) -> None:
        self.codigos_especiais = tuple(codigos_especiais)

    def fit(self, X: object, y: object = None) -> "ExtratorVar12Continua":
        """Valida a entrada; não aprende parâmetros."""

        self._extrair_serie(X)
        return self

    def transform(self, X: object) -> np.ndarray:
        """Retorna ``var12`` contínua com códigos especiais como ``NaN``."""

        serie = self._extrair_serie(X).astype(float).mask(
            lambda valores: valores.isin(self.codigos_especiais)
        )
        return serie.to_numpy().reshape(-1, 1)

    def get_feature_names_out(self, input_features: object = None) -> np.ndarray:
        """Retorna o nome estável da feature gerada."""

        return np.asarray(["var12_continua"], dtype=object)

    @staticmethod
    def _extrair_serie(X: object) -> pd.Series:
        quadro = pd.DataFrame(X)
        if quadro.shape[1] != 1:
            raise ValueError("ExtratorVar12Continua espera exatamente uma coluna.")
        return quadro.iloc[:, 0]


class IndicadoresEspeciaisVar12(BaseEstimator, TransformerMixin):
    """Implementa indicadores da representação histórica de ``var12``.

    Estes indicadores foram usados no desenvolvimento, mas não correspondem à
    especificação final baseada em ``var12_estado``.
    """

    def __init__(
        self,
        codigos_especiais: Iterable[int] = CODIGOS_ESPECIAIS_VAR12,
    ) -> None:
        self.codigos_especiais = tuple(codigos_especiais)

    def fit(self, X: object, y: object = None) -> "IndicadoresEspeciaisVar12":
        """Valida a entrada; não aprende parâmetros."""

        ExtratorVar12Continua._extrair_serie(X)
        return self

    def transform(self, X: object) -> np.ndarray:
        """Retorna uma coluna indicadora para cada código configurado."""

        serie = ExtratorVar12Continua._extrair_serie(X)
        return np.column_stack(
            [serie.eq(codigo).astype(np.int8) for codigo in self.codigos_especiais]
        )

    def get_feature_names_out(self, input_features: object = None) -> np.ndarray:
        """Retorna os nomes estáveis dos indicadores gerados."""

        return np.asarray(
            [f"var12_codigo_{codigo}" for codigo in self.codigos_especiais],
            dtype=object,
        )


def preparar_features_catboost(
    dados: pd.DataFrame,
    variaveis_numericas: list[str],
    variaveis_categoricas: list[str],
) -> pd.DataFrame:
    """Prepara a representação histórica para CatBoost sem aprender parâmetros.

    Os códigos especiais de ``var12`` são preservados em indicadores e removidos
    da componente contínua. Missing categórico vira rótulo explícito. Esta não é
    a especificação final baseada em ``var12_estado``.
    """

    colunas_necessarias = set(variaveis_numericas + variaveis_categoricas)
    ausentes = sorted(colunas_necessarias.difference(dados.columns))
    if ausentes:
        raise ValueError(f"Colunas ausentes para preparação: {ausentes}")

    resultado = dados[variaveis_numericas + variaveis_categoricas].copy()
    for codigo in CODIGOS_ESPECIAIS_VAR12:
        resultado[f"var12_codigo_{codigo}"] = resultado["var12"].eq(codigo).astype(int)
    resultado["var12"] = resultado["var12"].mask(
        resultado["var12"].isin(CODIGOS_ESPECIAIS_VAR12)
    )
    for variavel in variaveis_categoricas:
        resultado[variavel] = resultado[variavel].astype("string").fillna("__MISSING__")
    return resultado
