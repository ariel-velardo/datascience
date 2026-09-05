"""Tabela analitica curso x coorte para a AUDITORIA DE VIABILIDADE do Fies.

Somente construcao de tabela. Nao estima efeito causal, nao roda DiD.

Unidade: curso x coorte de ingresso, com outcome em HORIZONTE FIXO tau.
Isso evita o problema age-period-cohort do desenho COVID: todas as coortes
comparadas estao exatamente na mesma idade de trajetoria.

Populacao: cursos PRESENCIAIS de IES PRIVADAS (TP_CATEGORIA_ADMINISTRATIVA
in {4,5}) -- as unicas com Fies (categorias 1 e 2 tem QT_ING_FIES == 0 em
todos os anos).

Nota de dado [FATO]: no Censo slim (TP_DIMENSAO in {1,3}), TODA linha de EAD
(modalidade 2 / dimensao 3) tem QT_ING nulo -- os ingressantes de EAD estao
nas linhas de dimensao 2, descartadas. Logo share_fies so e computavel para
cursos presenciais.

Uso:
    python src/constroi_painel_fies.py
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

CENSO = Path("data/processed/modalidade_pre_covid_2015_2019.parquet")
TRAJ = Path("data/processed/trajetorias_2015_2020.parquet")
SAIDA = Path("data/processed/painel_fies_curso_coorte.parquet")

ANOS_PRE = [2015, 2016, 2017]   # coortes sob o Fies antigo
TAUS = [0, 1, 2, 3]


def exposicao() -> pd.DataFrame:
    """Exposicao ao Fies medida ANTES da reforma, no nivel do curso e da IES."""
    d = pd.read_parquet(CENSO)
    d = d[d.QT_ING.notna() & d.TP_CATEGORIA_ADMINISTRATIVA.isin([4, 5])].copy()
    d["share"] = np.where(d.QT_ING > 0, d.QT_ING_FIES / d.QT_ING, np.nan)
    d["share_prouni"] = np.where(
        d.QT_ING > 0, (d.QT_ING_PROUNII + d.QT_ING_PROUNIP) / d.QT_ING, np.nan)

    pre = d[d.NU_ANO_CENSO.isin(ANOS_PRE)]

    # --- curso
    w = pre.pivot_table(index="CO_CURSO", columns="NU_ANO_CENSO", values="share")
    cur = pd.DataFrame(index=w.index)
    cur["exp_fies_2015"] = w.get(2015)
    cur["exp_fies_1516"] = w[[2015, 2016]].mean(axis=1)
    cur["exp_fies_1517"] = w[[2015, 2016, 2017]].mean(axis=1)
    cur["n_anos_exp"] = w.notna().sum(axis=1)

    # ponderador de porte pre (media de ingressantes no pre)
    cur["ing_pre"] = pre.groupby("CO_CURSO").QT_ING.mean()
    cur["prouni_pre"] = (pre.pivot_table(index="CO_CURSO", columns="NU_ANO_CENSO",
                                         values="share_prouni")
                         [[2015, 2016, 2017]].mean(axis=1))

    # --- atributos de 2017 (ultimo ano pre-reforma), para estratificar
    a17 = (d[d.NU_ANO_CENSO == 2017]
           .set_index("CO_CURSO")[["CO_IES", "TP_CATEGORIA_ADMINISTRATIVA",
                                   "TP_ORGANIZACAO_ACADEMICA",
                                   "CO_CINE_AREA_GERAL", "CO_CINE_ROTULO",
                                   "CO_UF"]]
           .rename(columns=lambda c: c + "_2017"))
    cur = cur.join(a17, how="left")

    # --- exposicao agregada no nivel da IES (soma sobre cursos, pre-reforma)
    ies = (pre.groupby(["CO_IES"])[["QT_ING_FIES", "QT_ING"]].sum()
           .assign(exp_fies_ies=lambda x: x.QT_ING_FIES / x.QT_ING)
           ["exp_fies_ies"])
    cur = cur.join(ies, on="CO_IES_2017")

    # --- exposicao IES x area CINE
    iesa = (pre.groupby(["CO_IES", "CO_CINE_AREA_GERAL"])[["QT_ING_FIES", "QT_ING"]]
            .sum().assign(exp_fies_ies_area=lambda x: x.QT_ING_FIES / x.QT_ING)
            ["exp_fies_ies_area"])
    cur = cur.join(iesa, on=["CO_IES_2017", "CO_CINE_AREA_GERAL_2017"])

    # painel fechado do Censo (presente nos 5 anos, privado presencial)
    n5 = d.groupby("CO_CURSO").NU_ANO_CENSO.nunique()
    cur["censo_5anos"] = pd.Series(cur.index.map(n5), index=cur.index).fillna(0).astype(int).eq(5)
    return cur.reset_index()


def outcome() -> pd.DataFrame:
    """Desistencia acumulada em horizonte fixo tau, por curso x coorte."""
    t = pd.read_parquet(TRAJ, columns=[
        "CO_CURSO", "NU_ANO_INGRESSO", "IDADE_TRAJETORIA", "QT_INGRESSANTE",
        "CUM_DESISTENCIA", "CUM_CONCLUINTE", "CUM_FALECIDO"])
    t = t[t.IDADE_TRAJETORIA.isin(TAUS)].copy()
    t["base"] = t.QT_INGRESSANTE - t.CUM_FALECIDO
    t = t[t.base > 0].copy()
    t["desist_acum"] = 100.0 * t.CUM_DESISTENCIA / t.base
    t["conclui_acum"] = 100.0 * t.CUM_CONCLUINTE / t.base
    t["ano_calendario"] = t.NU_ANO_INGRESSO + t.IDADE_TRAJETORIA
    return t[["CO_CURSO", "NU_ANO_INGRESSO", "IDADE_TRAJETORIA", "ano_calendario",
              "QT_INGRESSANTE", "base", "desist_acum", "conclui_acum"]]


def main() -> None:
    cur = exposicao()
    out = outcome()
    p = out.merge(cur, on="CO_CURSO", how="inner")
    p["POS_REFORMA"] = (p.NU_ANO_INGRESSO >= 2018).astype(int)
    p["COVID"] = (p.ano_calendario >= 2020).astype(int)
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    p.to_parquet(SAIDA, index=False)

    print(f"-> {SAIDA}  {len(p):,} linhas  {p.CO_CURSO.nunique():,} cursos")
    print("\ncobertura por coorte x tau (cursos), privado presencial:")
    print(p.pivot_table(index="NU_ANO_INGRESSO", columns="IDADE_TRAJETORIA",
                        values="CO_CURSO", aggfunc="nunique").to_string())
    print("\nlinhas contaminadas por COVID (ano_calendario >= 2020):")
    print(p.groupby(["IDADE_TRAJETORIA", "NU_ANO_INGRESSO"]).COVID.max()
          .unstack().to_string())


if __name__ == "__main__":
    main()
