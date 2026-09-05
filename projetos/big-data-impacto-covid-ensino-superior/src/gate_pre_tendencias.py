"""GATE C3 — teste de pre-tendencias com tratamento predeterminado (pre-COVID).

Executa SOMENTE o teste de pre-tendencias. Nao estima o DiD final, nao faz
matching, nao produz estimativa de efeito causal. O unico coeficiente pos-2020
reportado e a "quebra de 2020", exigida pelo criterio do gate como referencia
de magnitude — e esta rotulada como tal.

Desenho (conforme docs/auditoria_causal_covid.md §9, versao estratificada por
idade de trajetoria):

  Para cada tau fixo, dentro de tau a coorte e o ano-calendario sao a mesma
  variavel (k = t - tau). O event study e, portanto, sobre coortes:

      h_{c,k} = alpha_{estrato x k} + sum_{j != ref} delta_j * Presencial_c * 1[k=j] + e

  Absorver o efeito fixo estrato x coorte faz com que apenas estratos que
  contenham AS DUAS modalidades naquela coorte contribuam — a comparacao e
  automaticamente within.

Outcome: hazard condicional de desistencia (nunca TDA nem TADA).
Inferencia: wild cluster bootstrap (Rademacher, nulo imposto) por IES.

Uso:
    python src/gate_pre_tendencias.py
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

PAINEL = Path("data/processed/painel_causal_pre_covid.parquet")
SAIDA = Path("data/processed/gate_pre_tendencias.json")

TAUS = [0, 1, 2]
B_BOOT = 9999
SEED = 20260904


# ----------------------------------------------------------------------
# Algebra: absorcao de efeitos fixos, WLS, cluster e wild bootstrap
# ----------------------------------------------------------------------

def demedia(M: np.ndarray, grupos: np.ndarray, w: np.ndarray) -> np.ndarray:
    """Remove a media ponderada por grupo (absorcao de um efeito fixo)."""
    M = np.asarray(M, dtype=float)
    if M.ndim == 1:
        M = M[:, None]
    soma_w = np.bincount(grupos, weights=w)
    out = np.empty_like(M)
    for j in range(M.shape[1]):
        soma = np.bincount(grupos, weights=w * M[:, j])
        out[:, j] = M[:, j] - (soma / soma_w)[grupos]
    return out


def wls(X: np.ndarray, y: np.ndarray, w: np.ndarray):
    sw = np.sqrt(w)
    Xw, yw = X * sw[:, None], y * sw
    XtX = Xw.T @ Xw
    XtXi = np.linalg.pinv(XtX)
    beta = XtXi @ (Xw.T @ yw)
    resid = y - X @ beta
    return beta, resid, XtXi


class Clusters:
    """Indices pre-computados para somas por cluster (reduceat vetorizado)."""

    def __init__(self, clusters: np.ndarray):
        self.ordem = np.argsort(clusters, kind="stable")
        cl = clusters[self.ordem]
        self.inicios = np.flatnonzero(np.r_[True, cl[1:] != cl[:-1]])
        self.G = len(self.inicios)

    def somas(self, A: np.ndarray) -> np.ndarray:
        return np.add.reduceat(A[self.ordem], self.inicios, axis=0)


def vcov_cluster(X, resid, w, cl: "Clusters", XtXi, k_extra=0):
    """CR1 cluster-robust para WLS, vetorizado por reduceat."""
    sw = np.sqrt(w)
    S = cl.somas((X * sw[:, None]) * (resid * sw)[:, None])
    meat = S.T @ S
    G = cl.G
    n, k = X.shape
    ajuste = (G / (G - 1)) * ((n - 1) / (n - k - k_extra)) if G > 1 else 1.0
    return XtXi @ meat @ XtXi * ajuste, G


def wald(beta, V, idx):
    b = beta[idx]
    Vs = V[np.ix_(idx, idx)]
    return float(b @ np.linalg.pinv(Vs) @ b)


def wild_bootstrap_conjunto(Xu, y, w, grupos, clusters, idx_restr,
                            B=B_BOOT, seed=SEED):
    """p-valor do teste conjunto H0: beta[idx_restr] = 0, via WCB-R.

    Impoe o nulo (estima o modelo restrito), reamostra os residuos com pesos
    de Rademacher por cluster e recompara a estatistica de Wald.

    Tudo o que nao depende de y* e pre-computado fora do laco: a matriz
    demediada, sua raiz ponderada, (X'WX)^-1 e a ordenacao por cluster.
    """
    rng = np.random.default_rng(seed)
    livres = [j for j in range(Xu.shape[1]) if j not in idx_restr]
    cl = Clusters(clusters)

    Xd = demedia(Xu, grupos, w)
    yd = demedia(y, grupos, w).ravel()
    sw = np.sqrt(w)
    Xw = Xd * sw[:, None]
    XtXi = np.linalg.pinv(Xw.T @ Xw)
    XtXi_Xw_T = XtXi @ Xw.T

    G = cl.G
    n, k = Xd.shape
    ajuste = (G / (G - 1)) * ((n - 1) / (n - k)) if G > 1 else 1.0
    ordem, inicios = cl.ordem, cl.inicios
    Xw_ord = Xw[ordem]
    sub = np.ix_(idx_restr, idx_restr)

    def estatistica(yd_local):
        beta = XtXi_Xw_T @ (yd_local * sw)
        uw = (yd_local - Xd @ beta) * sw
        S = np.add.reduceat(Xw_ord * uw[ordem][:, None], inicios, axis=0)
        V = XtXi @ (S.T @ S) @ XtXi * ajuste
        b = beta[idx_restr]
        return float(b @ np.linalg.pinv(V[sub]) @ b)

    W_obs = estatistica(yd)

    # Modelo restrito (leads = 0).
    if livres:
        Xr = Xd[:, livres]
        beta_r, _, _ = wls(Xr, yd, w)
        ajust_d = Xr @ beta_r
    else:
        ajust_d = np.zeros_like(yd)
    res_r_d = yd - ajust_d
    fe = y.ravel() - yd
    soma_w_g = np.bincount(grupos, weights=w)

    _, cl_idx = np.unique(clusters, return_inverse=True)
    n_cl = cl_idx.max() + 1
    maiores = 0
    for _ in range(B):
        sinal = rng.integers(0, 2, size=n_cl) * 2.0 - 1.0
        y_star = fe + ajust_d + sinal[cl_idx] * res_r_d
        yd_s = y_star - (np.bincount(grupos, weights=w * y_star)
                         / soma_w_g)[grupos]
        if estatistica(yd_s) >= W_obs:
            maiores += 1
    return W_obs, (1 + maiores) / (B + 1)


def n_efetivo(w: np.ndarray, clusters: np.ndarray) -> float:
    """Numero efetivo de clusters (Kish) dado o peso agregado por cluster."""
    s = pd.Series(w).groupby(clusters).sum().values
    return float(s.sum() ** 2 / (s ** 2).sum())


# ----------------------------------------------------------------------
# Montagem da amostra
# ----------------------------------------------------------------------

def carrega():
    cols = ["CO_CURSO", "CO_IES", "NU_ANO_INGRESSO", "NU_ANO_REFERENCIA",
            "IDADE_TRAJETORIA", "QT_DESISTENCIA", "QT_FALECIDO",
            "EM_RISCO_INICIO", "CLASSE_TRATAMENTO", "CO_IES_2019",
            "CATEGORIA_2019", "CINE_AREA_2019", "CINE_ROTULO_2019"]
    df = pd.read_parquet(PAINEL, columns=cols)
    df = df[df["CLASSE_TRATAMENTO"].isin(["presencial_estavel", "ead_estavel"])]
    df["PRESENCIAL"] = (df["CLASSE_TRATAMENTO"] == "presencial_estavel").astype(float)
    df["RISCO"] = df["EM_RISCO_INICIO"] - df["QT_FALECIDO"]
    df = df[df["RISCO"] > 0].copy()
    df["HAZARD"] = 100.0 * df["QT_DESISTENCIA"] / df["RISCO"]
    df["IES"] = df["CO_IES_2019"].fillna(df["CO_IES"]).astype("int64")
    return df


def define_estrato(d: pd.DataFrame, spec: str) -> np.ndarray:
    if spec == "S1_sem_estrato":
        base = pd.Series(0, index=d.index)
    elif spec == "S2_ies":
        base = d["IES"].astype(str)
    elif spec == "S3_ies_x_area":
        base = d["IES"].astype(str) + "|" + d["CINE_AREA_2019"].astype(str)
    elif spec == "S4_ies_x_rotulo":
        base = d["IES"].astype(str) + "|" + d["CINE_ROTULO_2019"].astype(str)
    elif spec == "S5_categoria_x_area":
        base = (d["CATEGORIA_2019"].astype(str) + "|"
                + d["CINE_AREA_2019"].astype(str))
    else:
        raise ValueError(spec)
    # O FE e sempre estrato x coorte: dentro de tau, coorte == ano-calendario.
    chave = base.astype(str) + "#" + d["NU_ANO_INGRESSO"].astype(str)
    return pd.factorize(chave)[0]


def roda(d: pd.DataFrame, tau: int, spec: str, coortes_pre, ref: int,
         incluir_pos: bool, ponderar: bool = True) -> dict:
    d = d[d["IDADE_TRAJETORIA"] == tau].copy()
    if not incluir_pos:
        d = d[d["NU_ANO_INGRESSO"].isin(coortes_pre)]
    d = d.sort_values(["CO_CURSO", "NU_ANO_INGRESSO"]).reset_index(drop=True)

    grupos = define_estrato(d, spec)
    w = (d["RISCO"].to_numpy(dtype=float) if ponderar
         else np.ones(len(d), dtype=float))

    # Mantem so estratos-coorte com as duas modalidades (identificacao within).
    g = pd.DataFrame({"g": grupos, "p": d["PRESENCIAL"].values})
    ok = g.groupby("g")["p"].transform("nunique").eq(2).values
    d, grupos, w = d[ok].reset_index(drop=True), grupos[ok], w[ok]
    if len(d) == 0:
        return {"erro": "sem estratos com as duas modalidades"}
    grupos = pd.factorize(grupos)[0]

    coortes = sorted(d["NU_ANO_INGRESSO"].unique())
    termos = [j for j in coortes if j != ref]
    pres_v = d["PRESENCIAL"].to_numpy(dtype=float)
    ano_v = d["NU_ANO_INGRESSO"].to_numpy()
    # Coluna 0 = efeito principal Presencial (o gap na coorte de referencia).
    # Sem ela, os coeficientes mediriam o NIVEL do gap em cada coorte, e nao o
    # desvio em relacao ao ano-base -- que e o que um event study reporta.
    X = np.column_stack(
        [pres_v] + [pres_v * (ano_v == j) for j in termos]).astype(float)
    y = d["HAZARD"].to_numpy(dtype=float)
    clusters = d["IES"].to_numpy()

    Xd = demedia(X, grupos, w)
    yd = demedia(y, grupos, w).ravel()
    beta, resid, XtXi = wls(Xd, yd, w)
    V, G = vcov_cluster(Xd, resid, w, Clusters(clusters), XtXi)
    se = np.sqrt(np.diag(V))

    idx_leads = [i + 1 for i, j in enumerate(termos) if j in coortes_pre]
    W, p = wild_bootstrap_conjunto(X, y, w, grupos, clusters, idx_leads)

    pres = d["PRESENCIAL"].values == 1
    res = {
        "tau": tau, "spec": spec, "ref": ref, "ponderado": ponderar,
        "inclui_pos_2020": incluir_pos,
        "N_linhas": int(len(d)),
        "N_cursos": int(d["CO_CURSO"].nunique()),
        "N_ies": int(d["IES"].nunique()),
        "N_estratos_coorte": int(len(np.unique(grupos))),
        "N_clusters_ies": int(G),
        "cursos_presencial": int(d.loc[pres, "CO_CURSO"].nunique()),
        "cursos_ead": int(d.loc[~pres, "CO_CURSO"].nunique()),
        "ies_presencial": int(d.loc[pres, "IES"].nunique()),
        "ies_ead": int(d.loc[~pres, "IES"].nunique()),
        "n_efetivo_ies_presencial": round(
            n_efetivo(w[pres], clusters[pres]), 1),
        "n_efetivo_ies_ead": round(n_efetivo(w[~pres], clusters[~pres]), 1),
        "coef": {}, "leads": [],
    }
    for i0, j in enumerate(termos):
        i = i0 + 1
        linha = {
            "coorte": int(j),
            "ano_calendario": int(j + tau),
            "papel": "LEAD (pre-2020)" if j in coortes_pre
                     else "QUEBRA/pos (referencia de magnitude, NAO e efeito)",
            "coef": round(float(beta[i]), 4),
            "se": round(float(se[i]), 4),
            "ic95": [round(float(beta[i] - 1.96 * se[i]), 4),
                     round(float(beta[i] + 1.96 * se[i]), 4)],
            "t": round(float(beta[i] / se[i]), 3) if se[i] > 0 else None,
        }
        res["coef"][str(int(j))] = linha
        if j in coortes_pre:
            res["leads"].append(linha)
    res["gap_na_coorte_de_referencia"] = {
        "coef": round(float(beta[0]), 4), "se": round(float(se[0]), 4)}
    res["teste_conjunto_leads"] = {
        "n_leads": len(idx_leads),
        "wald": round(W, 3),
        "p_wild_cluster_bootstrap": round(p, 5),
        "B": B_BOOT,
    }
    lm = [abs(l["coef"]) for l in res["leads"]]
    res["max_abs_lead"] = round(max(lm), 4) if lm else None
    res["dp_leads"] = round(float(np.std([l["coef"] for l in res["leads"]],
                                         ddof=1)), 4) if len(lm) > 1 else None
    return res


def main() -> None:
    d = carrega()
    print(f"amostra base: {len(d):,} linhas, "
          f"{d['CO_CURSO'].nunique():,} cursos com tratamento estavel")

    specs = ["S1_sem_estrato", "S2_ies", "S3_ies_x_area",
             "S4_ies_x_rotulo", "S5_categoria_x_area"]
    resultados = []
    for tau in TAUS:
        coortes_pre = [k for k in range(2015, 2021) if k + tau < 2020]
        ref = max(coortes_pre)
        print(f"\n=== tau={tau} | coortes pre: {coortes_pre} | ref={ref} "
              f"({len(coortes_pre)-1} leads) ===")
        for spec in specs:
            for incluir_pos in (False, True):
                r = roda(d, tau, spec, coortes_pre, ref, incluir_pos)
                if "erro" in r:
                    print(f"  {spec} pos={incluir_pos}: {r['erro']}")
                    continue
                resultados.append(r)
                tag = "pre+pos" if incluir_pos else "so pre"
                print(f"  {spec:<22} {tag:<8} N={r['N_linhas']:>7,} "
                      f"cursos={r['N_cursos']:>6,} IES={r['N_ies']:>4} "
                      f"Neff(EAD)={r['n_efetivo_ies_ead']:>6} "
                      f"max|lead|={r['max_abs_lead']:>7} "
                      f"p_conj={r['teste_conjunto_leads']['p_wild_cluster_bootstrap']:.4f}")
        # versao nao ponderada, so na especificacao principal
        r = roda(d, tau, "S3_ies_x_area", coortes_pre, ref, False,
                 ponderar=False)
        if "erro" not in r:
            r["spec"] = "S3_ies_x_area_NAO_PONDERADO"
            resultados.append(r)
            print(f"  {'S3 nao ponderado':<22} {'so pre':<8} "
                  f"N={r['N_linhas']:>7,} max|lead|={r['max_abs_lead']:>7} "
                  f"p_conj={r['teste_conjunto_leads']['p_wild_cluster_bootstrap']:.4f}")

    SAIDA.write_text(json.dumps(resultados, ensure_ascii=False, indent=1),
                     encoding="utf-8")
    print(f"\nresultados -> {SAIDA}")


if __name__ == "__main__":
    main()
