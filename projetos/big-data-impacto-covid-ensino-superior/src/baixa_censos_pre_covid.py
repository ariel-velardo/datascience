"""Aquisicao slim dos Censos da Educacao Superior 2015-2019 (cadastro de cursos).

Objetivo unico: obter a modalidade de ensino PRE-PANDEMIA por curso, para
construir um tratamento predeterminado. Nenhum ano >= 2020 e baixado.

Politica de disco, um ano por vez:
    download ZIP -> conferir MD5 publicado -> extrair SO o CSV de cursos
    -> documentar schema -> filtrar TP_DIMENSAO in (1,3) e projetar colunas
    -> gravar Parquet slim -> APAGAR CSV e ZIP

Pico transitorio: ZIP (<=17 MB) + CSV (<=143 MB). Residual: ~1 MB por ano.

Saidas:
    data/interim/censo_cursos_slim_{ano}.parquet
    data/interim/censo_schema_{ano}.json

Uso:
    python src/baixa_censos_pre_covid.py 2015 2016 2017 2018 2019
"""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

URL = ("https://download.inep.gov.br/microdados/"
       "microdados_censo_da_educacao_superior_{ano}.zip")

TMP = Path("data/interim/_censo_tmp")
SLIM = Path("data/interim")

# TP_DIMENSAO: 1 = presencial no Brasil, 2 = EAD replicado por municipio de
# oferta, 3 = EAD com dimensao apenas Brasil, 4 = EAD no exterior.
# Para um join em nivel de curso, so {1,3} interessa: {2} e replicacao
# geografica pura e inflaria o arquivo sem acrescentar cursos.
DIMENSOES = {1, 3}

COLUNAS = [
    # chave e tratamento
    "NU_ANO_CENSO", "CO_IES", "CO_CURSO", "TP_DIMENSAO",
    "TP_MODALIDADE_ENSINO",
    # estratificacao predeterminada
    "TP_CATEGORIA_ADMINISTRATIVA", "TP_ORGANIZACAO_ACADEMICA", "TP_REDE",
    "TP_GRAU_ACADEMICO", "TP_NIVEL_ACADEMICO", "IN_GRATUITO",
    # area e geografia
    "CO_CINE_ROTULO", "CO_CINE_AREA_GERAL", "CO_CINE_AREA_ESPECIFICA",
    "CO_REGIAO", "CO_UF", "CO_MUNICIPIO", "IN_CAPITAL",
    # seletividade
    "QT_VG_TOTAL", "QT_INSCRITO_TOTAL", "QT_ING",
    # turno
    "QT_ING_DIURNO", "QT_ING_NOTURNO", "QT_VG_TOTAL_NOTURNO",
    # financiamento e acao afirmativa
    "QT_ING_FIES", "QT_ING_PROUNII", "QT_ING_PROUNIP", "QT_ING_RESERVA_VAGA",
    # demografia de ingresso
    "QT_ING_FEM", "QT_ING_18_24", "QT_ING_25_29", "QT_ING_30_34",
    "QT_ING_35_39", "QT_ING_40_49", "QT_ING_50_59", "QT_ING_60_MAIS",
    "QT_ING_PRETA", "QT_ING_PARDA", "QT_ING_INDIGENA",
    "QT_ING_PROCESCPUBLICA",
    # situacao de vinculo
    "QT_SIT_TRANCADA", "QT_SIT_DESVINCULADO", "QT_SIT_TRANSFERIDO",
]

# Codigos CINE tem zero a esquerda -> texto, sempre.
TEXTO = {"CO_CINE_ROTULO", "CO_CINE_AREA_GERAL", "CO_CINE_AREA_ESPECIFICA"}


def md5(caminho: Path, blocos: int = 1 << 20) -> str:
    h = hashlib.md5()
    with caminho.open("rb") as f:
        for bloco in iter(lambda: f.read(blocos), b""):
            h.update(bloco)
    return h.hexdigest()


def baixa(url: str, destino: Path) -> None:
    """curl com verificacao TLS ativa (o host omite o intermediario da cadeia,
    o que quebra o OpenSSL do Python mas nao o schannel do curl)."""
    r = subprocess.run(
        ["curl", "--fail", "--location", "--show-error", "--silent",
         "--retry", "3", "--retry-delay", "5", "-A", "Mozilla/5.0",
         "-o", str(destino), url],
        capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"curl falhou ({r.returncode}): {r.stderr}")


def processa(ano: int) -> dict:
    assert ano <= 2019, "nenhum ano >= 2020 pode entrar no tratamento"
    saida = SLIM / f"censo_cursos_slim_{ano}.parquet"
    relatorio = SLIM / f"censo_schema_{ano}.json"

    print("=" * 78)
    print(f"CENSO {ano}")
    if saida.exists():
        print(f"  {saida.name} ja existe; pulando.")
        return json.loads(relatorio.read_text(encoding="utf-8"))

    TMP.mkdir(parents=True, exist_ok=True)
    zip_path = TMP / f"censo_{ano}.zip"

    if not zip_path.exists():
        print("  baixando...")
        baixa(URL.format(ano=ano), zip_path)
    aud = {"ano": ano, "url": URL.format(ano=ano),
           "zip_mb": round(zip_path.stat().st_size / 1e6, 2),
           "zip_md5": md5(zip_path)}
    print(f"  ZIP {aud['zip_mb']} MB")

    # Extrai SOMENTE o cadastro de cursos e o md5 publicado.
    with zipfile.ZipFile(zip_path) as z:
        nomes = z.namelist()
        alvo = [n for n in nomes
                if n.upper().endswith(f"MICRODADOS_CADASTRO_CURSOS_{ano}.CSV")]
        md5pub = [n for n in nomes if n.lower().endswith(".txt")
                  and "md5" in n.lower()]
        assert len(alvo) == 1, f"cadastro de cursos ambiguo: {alvo}"
        aud["membro_extraido"] = alvo[0]
        aud["tamanho_descomprimido_mb"] = round(
            z.getinfo(alvo[0]).file_size / 1e6, 2)
        csv_path = TMP / f"cursos_{ano}.csv"
        with z.open(alvo[0]) as origem, csv_path.open("wb") as destino:
            shutil.copyfileobj(origem, destino)
        aud["md5_publicado_confere"] = None
        for nome in md5pub:
            texto = z.read(nome).decode("utf-8", errors="replace")
            for linha in texto.splitlines():
                if f"CURSOS_{ano}" in linha.upper():
                    aud["md5_publicado_linha"] = linha.strip()
                    aud["md5_publicado_confere"] = (
                        linha.split()[0].lower() == md5(csv_path))
    print(f"  CSV extraido: {aud['tamanho_descomprimido_mb']} MB  "
          f"md5 publicado confere: {aud['md5_publicado_confere']}")

    # --- Documentacao do schema, ANTES de processar ---
    with csv_path.open("r", encoding="latin-1") as f:
        cabecalho = f.readline().rstrip("\n").rstrip("\r").split(";")
    aud["n_colunas"] = len(cabecalho)
    aud["colunas"] = cabecalho
    aud["colunas_pedidas_ausentes"] = [c for c in COLUNAS
                                       if c not in cabecalho]
    print(f"  schema: {aud['n_colunas']} colunas; "
          f"ausentes das pedidas: {aud['colunas_pedidas_ausentes'] or 'nenhuma'}")

    usar = [c for c in COLUNAS if c in cabecalho]
    df = pd.read_csv(csv_path, sep=";", encoding="latin-1", usecols=usar,
                     dtype={c: "string" for c in TEXTO if c in usar},
                     low_memory=False)
    aud["linhas_csv"] = int(len(df))
    aud["cursos_distintos_csv"] = int(df["CO_CURSO"].nunique())
    aud["tp_dimensao"] = {str(int(k)): int(v) for k, v in
                          df["TP_DIMENSAO"].value_counts().items()}

    df = df[df["TP_DIMENSAO"].isin(DIMENSOES)].copy()
    aud["linhas_apos_filtro_dimensao"] = int(len(df))
    aud["cursos_distintos_apos_filtro"] = int(df["CO_CURSO"].nunique())
    aud["co_curso_unico_apos_filtro"] = bool(
        not df["CO_CURSO"].duplicated().any())
    aud["co_curso_determina_co_ies"] = bool(
        df.groupby("CO_CURSO")["CO_IES"].nunique().eq(1).all())
    aud["modalidade"] = {str(int(k)): int(v) for k, v in
                         df["TP_MODALIDADE_ENSINO"].value_counts().items()}

    # Codigos CINE: preservar zero a esquerda e remover aspas duplicadas
    # que o Inep emite em alguns anos ("""0721E01""").
    for c in TEXTO:
        if c in df.columns:
            df[c] = df[c].str.replace('"', "", regex=False).str.strip()

    SLIM.mkdir(parents=True, exist_ok=True)
    pq.write_table(pa.Table.from_pandas(df, preserve_index=False), saida,
                   compression="zstd")
    aud["parquet_mb"] = round(saida.stat().st_size / 1e6, 3)
    relatorio.write_text(json.dumps(aud, ensure_ascii=False, indent=1),
                         encoding="utf-8")

    # --- Limpeza ---
    csv_path.unlink()
    zip_path.unlink()
    print(f"  Parquet slim: {aud['parquet_mb']} MB "
          f"({aud['cursos_distintos_apos_filtro']:,} cursos)")
    print(f"  apagados: censo_{ano}.zip ({aud['zip_mb']} MB) e "
          f"cursos_{ano}.csv ({aud['tamanho_descomprimido_mb']} MB)")
    return aud


if __name__ == "__main__":
    anos = [int(a) for a in sys.argv[1:]] or [2015, 2016, 2017, 2018, 2019]
    auds = [processa(a) for a in anos]
    if TMP.exists() and not any(TMP.iterdir()):
        TMP.rmdir()
    print("\n" + "=" * 78)
    print(f"{'ano':>5} {'colunas':>8} {'linhas':>10} {'cursos':>8} "
          f"{'parquet MB':>11} {'md5 ok':>7}")
    for a in auds:
        print(f"{a['ano']:>5} {a['n_colunas']:>8} "
              f"{a['linhas_apos_filtro_dimensao']:>10,} "
              f"{a['cursos_distintos_apos_filtro']:>8,} "
              f"{a['parquet_mb']:>11} {str(a['md5_publicado_confere']):>7}")
