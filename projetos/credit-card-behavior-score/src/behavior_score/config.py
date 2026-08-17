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

# Universo histórico avaliado durante a exploração e o desenvolvimento.
# Estas constantes não representam a especificação final do modelo.
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

# Especificação final aprovada antes da avaliação OOT.
FEATURES_FINAIS_ORIGINAIS = [
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

FEATURES_REMOVIDAS = [
    "cat_var6",
    "cat_var13",
]

VARIAVEIS_NUMERICAS_FINAIS = [
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

VARIAVEIS_CATEGORICAS_FINAIS = [
    "cat_var2",
    "cat_var10",
    "cat_var15",
]

VARIAVEIS_MODELO_FINAL = (
    VARIAVEIS_NUMERICAS_FINAIS
    + VARIAVEIS_CATEGORICAS_FINAIS
    + ["var12_estado"]
)

COLUNAS_CONTROLE = [
    COLUNA_INDICE,
    COLUNA_ID,
    COLUNA_SAFRA,
    ALVO,
]
