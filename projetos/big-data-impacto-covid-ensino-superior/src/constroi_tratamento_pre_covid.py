"""Tratamento predeterminado (pre-COVID) e painel causal.

Etapas:
 4. tabela longitudinal pre-COVID por curso (Censos 2015-2019, so ate 2019);
 5. auditoria de estabilidade da modalidade 2015-2019 e classificacao;
 6. integracao ao painel de trajetorias, SEM sobrescrever o original.

Saidas:
    data/processed/modalidade_pre_covid_2015_2019.parquet   (curso x ano)
    data/processed/tratamento_pre_covid.parquet             (curso, 1 linha)
    data/processed/painel_causal_pre_covid.parquet          (painel integrado)
    data/processed/auditoria_tratamento_pre_covid.json

Nenhuma informacao de 2020 ou posterior entra na definicao do tratamento.
"""

from __future__ import annotations

import json
from pathlib import Path

import duckdb
import pandas as pd

ANOS = [2015, 2016, 2017, 2018, 2019]
INTERIM = Path("data/interim")
PROC = Path("data/processed")
PAINEL = PROC / "trajetorias_2015_2020.parquet"

LONGA = PROC / "modalidade_pre_covid_2015_2019.parquet"
TRAT = PROC / "tratamento_pre_covid.parquet"
SAIDA = PROC / "painel_causal_pre_covid.parquet"
RELATORIO = PROC / "auditoria_tratamento_pre_covid.json"

COLS_LONGA = [
    "CO_CURSO", "CO_IES", "NU_ANO_CENSO", "TP_MODALIDADE_ENSINO",
    "TP_CATEGORIA_ADMINISTRATIVA", "TP_ORGANIZACAO_ACADEMICA",
    "TP_GRAU_ACADEMICO", "CO_CINE_ROTULO", "CO_CINE_AREA_GERAL",
    "CO_REGIAO", "CO_UF", "QT_ING", "QT_VG_TOTAL", "QT_INSCRITO_TOTAL",
    "QT_ING_NOTURNO", "QT_ING_FIES", "QT_ING_PROUNII", "QT_ING_PROUNIP",
]


def main() -> None:
    con = duckdb.connect()
    aud: dict = {"anos_censo_usados": ANOS,
                 "regra": "nenhuma informacao de 2020+ entra no tratamento"}

    # ---------- Etapa 4: tabela longitudinal pre-COVID ----------
    for a in ANOS:
        con.execute(f"CREATE VIEW c{a} AS SELECT * FROM "
                    f"read_parquet('{INTERIM}/censo_cursos_slim_{a}.parquet')")
    uniao = " UNION ALL ".join(
        f"SELECT {', '.join(COLS_LONGA)} FROM c{a}" for a in ANOS)
    con.execute(f"CREATE VIEW longa AS {uniao}")
    longa = con.execute("SELECT * FROM longa ORDER BY CO_CURSO, NU_ANO_CENSO").df()
    longa.to_parquet(LONGA, compression="zstd", index=False)

    aud["longa"] = {
        "linhas": int(len(longa)),
        "cursos": int(longa["CO_CURSO"].nunique()),
        "ies": int(longa["CO_IES"].nunique()),
        "anos": sorted(longa["NU_ANO_CENSO"].unique().tolist()),
        "parquet_mb": round(LONGA.stat().st_size / 1e6, 3),
        "chave_curso_ano_unica": bool(
            not longa.duplicated(["CO_CURSO", "NU_ANO_CENSO"]).any()),
    }

    # ---------- Etapa 5: estabilidade da modalidade ----------
    g = longa.groupby("CO_CURSO")
    est = pd.DataFrame({
        "n_anos": g["NU_ANO_CENSO"].nunique(),
        "n_modalidades": g["TP_MODALIDADE_ENSINO"].nunique(),
        "modalidade_min": g["TP_MODALIDADE_ENSINO"].min(),
        "primeiro_ano": g["NU_ANO_CENSO"].min(),
        "ultimo_ano": g["NU_ANO_CENSO"].max(),
    }).reset_index()

    # Modalidade em 2019 (definicao B da auditoria: data unica, pre-choque).
    m2019 = (longa[longa["NU_ANO_CENSO"] == 2019]
             [["CO_CURSO", "TP_MODALIDADE_ENSINO", "CO_IES",
               "TP_CATEGORIA_ADMINISTRATIVA", "TP_ORGANIZACAO_ACADEMICA",
               "TP_GRAU_ACADEMICO", "CO_CINE_ROTULO", "CO_CINE_AREA_GERAL",
               "QT_ING", "QT_VG_TOTAL", "QT_INSCRITO_TOTAL"]]
             .rename(columns={
                 "TP_MODALIDADE_ENSINO": "MODALIDADE_2019",
                 "CO_IES": "CO_IES_2019",
                 "TP_CATEGORIA_ADMINISTRATIVA": "CATEGORIA_2019",
                 "TP_ORGANIZACAO_ACADEMICA": "ORGANIZACAO_2019",
                 "TP_GRAU_ACADEMICO": "GRAU_2019",
                 "CO_CINE_ROTULO": "CINE_ROTULO_2019",
                 "CO_CINE_AREA_GERAL": "CINE_AREA_2019",
                 "QT_ING": "QT_ING_2019", "QT_VG_TOTAL": "QT_VG_2019",
                 "QT_INSCRITO_TOTAL": "QT_INSC_2019"}))
    est = est.merge(m2019, on="CO_CURSO", how="left")

    # Modalidade no primeiro ano observado (definicao A, sensibilidade).
    prim = (longa.sort_values("NU_ANO_CENSO").groupby("CO_CURSO").first()
            [["TP_MODALIDADE_ENSINO"]]
            .rename(columns={"TP_MODALIDADE_ENSINO": "MODALIDADE_PRIMEIRO_ANO"})
            .reset_index())
    est = est.merge(prim, on="CO_CURSO", how="left")

    # Classificacao. "Suficiente" = >= 2 anos observados no periodo pre-COVID
    # E modalidade conhecida em 2019 (a data de referencia do tratamento).
    def classifica(r):
        if pd.isna(r["MODALIDADE_2019"]) or r["n_anos"] < 2:
            return "sem_informacao_suficiente"
        if r["n_modalidades"] > 1:
            return "mudou_de_modalidade"
        return ("presencial_estavel" if r["modalidade_min"] == 1
                else "ead_estavel")

    est["CLASSE_TRATAMENTO"] = est.apply(classifica, axis=1)
    est["TRATAMENTO_ESTAVEL"] = est["CLASSE_TRATAMENTO"].isin(
        ["presencial_estavel", "ead_estavel"])
    est.to_parquet(TRAT, compression="zstd", index=False)

    aud["classificacao"] = {
        k: int(v) for k, v in est["CLASSE_TRATAMENTO"].value_counts().items()}
    aud["cursos_por_n_anos_observados"] = {
        str(k): int(v) for k, v in est["n_anos"].value_counts().sort_index().items()}
    aud["mudou_de_modalidade_detalhe"] = {
        "total": int((est.CLASSE_TRATAMENTO == "mudou_de_modalidade").sum()),
        "presencial_para_ead": int(
            ((est.CLASSE_TRATAMENTO == "mudou_de_modalidade")
             & (est.MODALIDADE_PRIMEIRO_ANO == 1)
             & (est.MODALIDADE_2019 == 2)).sum()),
        "ead_para_presencial": int(
            ((est.CLASSE_TRATAMENTO == "mudou_de_modalidade")
             & (est.MODALIDADE_PRIMEIRO_ANO == 2)
             & (est.MODALIDADE_2019 == 1)).sum()),
    }

    # ---------- Etapa 6: integracao ao painel ----------
    con.execute(f"CREATE VIEW traj AS SELECT * FROM read_parquet('{PAINEL}')")
    con.register("trat", est)

    painel = con.execute("""
        SELECT t.*,
               tr.MODALIDADE_2019, tr.MODALIDADE_PRIMEIRO_ANO,
               tr.CLASSE_TRATAMENTO, tr.TRATAMENTO_ESTAVEL,
               tr.n_anos      AS N_ANOS_CENSO_PRE,
               tr.CO_IES_2019, tr.CATEGORIA_2019, tr.ORGANIZACAO_2019,
               tr.GRAU_2019, tr.CINE_ROTULO_2019, tr.CINE_AREA_2019,
               tr.QT_ING_2019, tr.QT_VG_2019, tr.QT_INSC_2019
        FROM traj t LEFT JOIN trat tr USING (CO_CURSO)
    """).df()
    painel["CLASSE_TRATAMENTO"] = painel["CLASSE_TRATAMENTO"].fillna(
        "ausente_no_censo_pre_covid")
    painel["TRATAMENTO_ESTAVEL"] = painel["TRATAMENTO_ESTAVEL"].fillna(False)
    painel.to_parquet(SAIDA, compression="zstd", index=False)

    cursos_painel = con.execute(
        "SELECT count(DISTINCT CO_CURSO) n FROM traj").df().n[0]
    cob = con.execute("""
        SELECT count(DISTINCT t.CO_CURSO) n FROM traj t
        JOIN trat tr USING (CO_CURSO)""").df().n[0]
    aud["integracao"] = {
        "cursos_no_painel": int(cursos_painel),
        "cursos_com_tratamento_pre_covid": int(cob),
        "cobertura_pct": round(100 * cob / cursos_painel, 2),
        "linhas_painel": int(len(painel)),
        "parquet_mb": round(SAIDA.stat().st_size / 1e6, 2),
        "original_preservado": PAINEL.exists(),
    }
    aud["classe_por_curso_no_painel"] = {
        k: int(v) for k, v in
        painel.groupby("CO_CURSO")["CLASSE_TRATAMENTO"].first()
        .value_counts().items()}

    # Concordancia entre o snapshot 2024 do painel e a modalidade de 2019.
    conc = con.execute("""
        WITH tc AS (SELECT DISTINCT CO_CURSO, TP_MODALIDADE_ENSINO m24 FROM traj)
        SELECT sum(CASE WHEN tc.m24 = tr.MODALIDADE_2019 THEN 1 ELSE 0 END) igual,
               count(*) total
        FROM tc JOIN trat tr USING (CO_CURSO)
        WHERE tr.MODALIDADE_2019 IS NOT NULL""").df()
    aud["snapshot2024_vs_2019"] = {
        "cursos_comparados": int(conc.total[0]),
        "concordam": int(conc.igual[0]),
        "pct": round(100 * conc.igual[0] / conc.total[0], 3),
    }

    RELATORIO.write_text(json.dumps(aud, ensure_ascii=False, indent=1),
                         encoding="utf-8")
    print(json.dumps(aud, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
