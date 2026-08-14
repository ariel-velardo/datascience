"""Configurações centrais do projeto."""

from pathlib import Path


RAIZ_PROJETO = Path(__file__).resolve().parents[2]

PASTA_DADOS = RAIZ_PROJETO / "data"
PASTA_DADOS_BRUTOS = PASTA_DADOS / "raw"
PASTA_DADOS_INTERMEDIARIOS = PASTA_DADOS / "interim"
PASTA_DADOS_PROCESSADOS = PASTA_DADOS / "processed"

PASTA_ARTEFATOS = RAIZ_PROJETO / "artifacts"
PASTA_MODELOS = PASTA_ARTEFATOS / "models"
PASTA_METRICAS = PASTA_ARTEFATOS / "metrics"

PASTA_RELATORIOS = RAIZ_PROJETO / "reports"
PASTA_FIGURAS = PASTA_RELATORIOS / "figures"
PASTA_TABELAS = PASTA_RELATORIOS / "tables"

ALVO = "Ever30Mob6"
COLUNA_SAFRA = "data_ref_safra"
COLUNA_ID = "id"
COLUNA_INDICE = "index"

SEMENTE_ALEATORIA = 42

VARIAVEIS_NUMERICAS = [
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
]

VARIAVEIS_CATEGORICAS = [
    "cat_var2",
    "cat_var6",
    "cat_var10",
    "cat_var13",
    "cat_var15",
]

VARIAVEIS_MODELO = (
    VARIAVEIS_NUMERICAS
    + VARIAVEIS_CATEGORICAS
)

COLUNAS_CONTROLE = [
    COLUNA_INDICE,
    COLUNA_ID,
    COLUNA_SAFRA,
    ALVO,
]
