from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path.cwd()
if ROOT.name in {"scripts", "notebooks"}:
    ROOT = ROOT.parent

TABLES = ROOT / "outputs" / "tables"
PROCESSED = ROOT / "data" / "processed"

TABLES.mkdir(parents=True, exist_ok=True)

BASE_SIM = PROCESSED / "base_simulacao_cenarios_politica.parquet"
BASE_SCORE = PROCESSED / "base_politica_validacao_com_score.parquet"

CENARIO_RECOMENDADO = "Expansivo controlado"
DEC_APROVADAS = ["Aprovar valor solicitado", "Aprovar valor reduzido"]
DEC_MANUAL = "Análise manual"
DEC_RECUSA = "Recusar"

ORDEM_RATING = [
    "A - Baixo risco",
    "B - Médio-baixo risco",
    "C - Médio risco",
    "D - Alto risco",
    "E - Muito alto risco",
]

def ordenar_rating(df, col="faixa_risco"):
    if col in df.columns:
        df[col] = pd.Categorical(df[col], categories=ORDEM_RATING, ordered=True)
        df = df.sort_values(col)
        df[col] = df[col].astype(str)
    return df

def media_ponderada(df, valor_col, peso_col):
    tmp = df[[valor_col, peso_col]].copy()
    tmp[valor_col] = pd.to_numeric(tmp[valor_col], errors="coerce")
    tmp[peso_col] = pd.to_numeric(tmp[peso_col], errors="coerce")
    tmp = tmp.dropna()
    tmp = tmp[tmp[peso_col] > 0]
    if len(tmp) == 0:
        return np.nan
    return float(np.average(tmp[valor_col], weights=tmp[peso_col]))

def taxa_aprovacao_auto(s):
    return s.isin(DEC_APROVADAS).mean()

def classificar_restritivo_ratio(x):
    if pd.isna(x) or x <= 0:
        return "sem_restritivo"
    if x <= 0.02:
        return "ate_2pct"
    if x <= 0.05:
        return "ate_5pct"
    if x <= 0.10:
        return "ate_10pct"
    return "acima_10pct"

print("=" * 90)
print("GERAÇÃO DE AUDITORIAS COMPLEMENTARES — POLÍTICA V14")
print("=" * 90)

if not BASE_SIM.exists():
    raise FileNotFoundError(f"Base simulada não encontrada: {BASE_SIM}")

if not BASE_SCORE.exists():
    raise FileNotFoundError(f"Base com score não encontrada: {BASE_SCORE}")

base_sim = pd.read_parquet(BASE_SIM)
base_score = pd.read_parquet(BASE_SCORE)

required_sim = [
    "cenario",
    "faixa_risco",
    "pd_score",
    "valor_emprestado",
    "valor_aprovado_cenario",
    "decisao_cenario",
    "target_inadimplente_12m",
]

missing = [c for c in required_sim if c not in base_sim.columns]
if missing:
    raise ValueError(f"Colunas ausentes na base simulada: {missing}")

if "id_operacao" not in base_sim.columns:
    base_sim = base_sim.copy()
    base_sim["id_operacao"] = np.arange(len(base_sim))

if "id_operacao" not in base_score.columns:
    base_score = base_score.copy()
    base_score["id_operacao"] = np.arange(len(base_score))

if "classe_restritivo_cenario" not in base_sim.columns:
    base_sim["classe_restritivo_cenario"] = base_sim["restritivos_sobre_renda"].apply(classificar_restritivo_ratio)

exp = base_sim[base_sim["cenario"] == CENARIO_RECOMENDADO].copy()

print(f"\nBase simulada: {len(base_sim):,} linhas")
print(f"Base do cenário recomendado: {len(exp):,} operações")

# ============================================================
# 1. Comprometimento histórico vs teto da política
# ============================================================

print("\n1) Gerando politica_comprometimento_historico_vs_teto.csv")

if "comprometimento_renda" not in base_score.columns:
    raise ValueError("Coluna comprometimento_renda ausente em base_score.")

if "pct_max_comprometimento_cenario" not in exp.columns:
    raise ValueError("Coluna pct_max_comprometimento_cenario ausente em base_sim.")

hist_comp = (
    base_score
    .groupby("faixa_risco", as_index=False)
    .agg(
        qtd_operacoes=("id_operacao", "count"),
        comprometimento_historico_mediano=("comprometimento_renda", "median"),
        comprometimento_historico_medio=("comprometimento_renda", "mean"),
    )
)

param_comp = (
    exp
    .groupby("faixa_risco", as_index=False)
    .agg(
        pct_max_comprometimento_politica=("pct_max_comprometimento_cenario", "first")
    )
)

comp = hist_comp.merge(param_comp, on="faixa_risco", how="left")
comp["diferenca_pp"] = (
    comp["pct_max_comprometimento_politica"]
    - comp["comprometimento_historico_mediano"]
)

def leitura_comp(row):
    r = str(row["faixa_risco"])
    if r.startswith("A"):
        return "Rating de menor risco; política permite maior comprometimento automático com teto e limite."
    if r.startswith("B"):
        return "Política reduz alavancagem automática frente ao comprometimento histórico elevado."
    if r.startswith("C"):
        return "Política reduz alavancagem e direciona a maior parte do grupo para controles/mesa."
    if r.startswith("D"):
        return "Sem limite automático; análise manual é mais prudente dado comprometimento histórico elevado."
    if r.startswith("E"):
        return "Recusa automática; alto risco e comprometimento histórico elevado."
    return ""

comp["leitura_politica"] = comp.apply(leitura_comp, axis=1)
comp = ordenar_rating(comp)

comp.to_csv(
    TABLES / "politica_comprometimento_historico_vs_teto.csv",
    index=False,
    encoding="utf-8-sig",
)

print(comp.to_string(index=False))

# ============================================================
# 2. Backtest integral vs reduzido
# ============================================================

print("\n2) Gerando politica_backtest_integral_reduzido.csv")

backtest = (
    exp
    .groupby("decisao_cenario", as_index=False)
    .agg(
        qtd_operacoes=("id_operacao", "count"),
        valor_solicitado_total=("valor_emprestado", "sum"),
        valor_aprovado_total=("valor_aprovado_cenario", "sum"),
        bad_rate_observado=("target_inadimplente_12m", "mean"),
        pd_media=("pd_score", "mean"),
    )
)

backtest["perc_operacoes"] = backtest["qtd_operacoes"] / len(exp)

pond_dec = []
for decisao, g in exp.groupby("decisao_cenario"):
    pond_dec.append({
        "decisao_cenario": decisao,
        "pd_media_ponderada_valor_aprovado": media_ponderada(g, "pd_score", "valor_aprovado_cenario"),
        "target_ponderado_valor_aprovado": media_ponderada(g, "target_inadimplente_12m", "valor_aprovado_cenario"),
    })

pond_dec = pd.DataFrame(pond_dec)
backtest = backtest.merge(pond_dec, on="decisao_cenario", how="left")

backtest["observacao"] = np.where(
    backtest["decisao_cenario"].eq("Aprovar valor reduzido"),
    "Desfecho observado pertence à operação originalmente concedida; performance da operação reduzida deve ser validada em piloto.",
    "Backtest histórico da decisão simulada.",
)

ordem_dec = [
    "Aprovar valor solicitado",
    "Aprovar valor reduzido",
    "Análise manual",
    "Recusar",
]

backtest["decisao_cenario"] = pd.Categorical(
    backtest["decisao_cenario"],
    categories=ordem_dec,
    ordered=True,
)
backtest = backtest.sort_values("decisao_cenario")
backtest["decisao_cenario"] = backtest["decisao_cenario"].astype(str)

backtest.to_csv(
    TABLES / "politica_backtest_integral_reduzido.csv",
    index=False,
    encoding="utf-8-sig",
)

print(backtest.to_string(index=False))

# ============================================================
# 3. Risco ponderado por exposição
# ============================================================

print("\n3) Gerando politica_risco_ponderado_exposicao.csv")

risco_rows = []

for cenario, g in base_sim.groupby("cenario"):
    aprov = g[g["decisao_cenario"].isin(DEC_APROVADAS)].copy()
    risco_rows.append({
        "cenario": cenario,
        "qtd_operacoes": len(g),
        "qtd_aprovados": len(aprov),
        "valor_solicitado_total": g["valor_emprestado"].sum(),
        "valor_aprovado_total": g["valor_aprovado_cenario"].sum(),
        "pct_exposicao_aprovada": g["valor_aprovado_cenario"].sum() / g["valor_emprestado"].sum(),
        "bad_rate_aprovados_por_operacao": aprov["target_inadimplente_12m"].mean() if len(aprov) else np.nan,
        "pd_media_aprovados": aprov["pd_score"].mean() if len(aprov) else np.nan,
        "pd_media_ponderada_valor_aprovado": media_ponderada(aprov, "pd_score", "valor_aprovado_cenario"),
        "target_ponderado_valor_aprovado": media_ponderada(aprov, "target_inadimplente_12m", "valor_aprovado_cenario"),
        "observacao": "Bad rate por operação mede incidência nos aprovados; métricas ponderadas por valor aprovado acompanham risco de exposição."
    })

risco = pd.DataFrame(risco_rows)
risco.to_csv(
    TABLES / "politica_risco_ponderado_exposicao.csv",
    index=False,
    encoding="utf-8-sig",
)

print(risco.to_string(index=False))

# ============================================================
# 4. Mesa operacional
# ============================================================

print("\n4) Gerando politica_mesa_operacional.csv")

manual = base_sim[base_sim["decisao_cenario"].eq(DEC_MANUAL)].copy()

mesa = (
    manual
    .groupby(["cenario", "faixa_risco"], as_index=False)
    .agg(
        qtd_manual=("id_operacao", "count"),
        valor_solicitado_manual=("valor_emprestado", "sum"),
        pd_media_manual=("pd_score", "mean"),
        bad_rate_manual=("target_inadimplente_12m", "mean"),
    )
)

tot_rating = (
    base_sim
    .groupby(["cenario", "faixa_risco"], as_index=False)
    .agg(qtd_rating=("id_operacao", "count"))
)

mesa = mesa.merge(tot_rating, on=["cenario", "faixa_risco"], how="left")
mesa["perc_manual_no_rating"] = mesa["qtd_manual"] / mesa["qtd_rating"]

def leitura_mesa(row):
    if row["qtd_manual"] == 0:
        return "Sem volume relevante em mesa."
    return "Volume exige dimensionamento operacional antes de piloto/rollout."

mesa["leitura_operacional"] = mesa.apply(leitura_mesa, axis=1)
mesa = ordenar_rating(mesa)

mesa.to_csv(
    TABLES / "politica_mesa_operacional.csv",
    index=False,
    encoding="utf-8-sig",
)

print(mesa[mesa["cenario"].eq(CENARIO_RECOMENDADO)].to_string(index=False))

# ============================================================
# 5. Restritivo severo em A/B
# ============================================================

print("\n5) Gerando politica_restritivo_severo_ab.csv")

if "restritivos_sobre_renda" not in exp.columns:
    raise ValueError("Coluna restritivos_sobre_renda ausente em base_sim.")

mask_ab = exp["faixa_risco"].astype(str).str.startswith(("A", "B"))
mask_severo = exp["restritivos_sobre_renda"].fillna(0) > 0.10
ab_severo = exp[mask_ab & mask_severo].copy()

restr_ab = (
    ab_severo
    .groupby(["faixa_risco"], as_index=False)
    .agg(
        qtd_operacoes=("id_operacao", "count"),
        qtd_aprovacao_automatica=("decisao_cenario", lambda s: s.isin(DEC_APROVADAS).sum()),
        valor_aprovado_total=("valor_aprovado_cenario", "sum"),
        pd_media=("pd_score", "mean"),
        bad_rate_observado=("target_inadimplente_12m", "mean"),
        restritivos_sobre_renda_medio=("restritivos_sobre_renda", "mean"),
    )
)

restr_ab["leitura_risco"] = (
    "Grupo A/B com restritivo >10% da renda. Política atual reduz limite, mas evolução possível é envio à mesa."
)

restr_ab = ordenar_rating(restr_ab)

restr_ab.to_csv(
    TABLES / "politica_restritivo_severo_ab.csv",
    index=False,
    encoding="utf-8-sig",
)

print(restr_ab.to_string(index=False))

# ============================================================
# 6. Sensibilidade: trava restritivo severo em A/B
# ============================================================

print("\n6) Gerando politica_sensibilidade_trava_restritivo_severo.csv")

def resumo_cenario_df(df, nome):
    aprov = df[df["decisao_cenario"].isin(DEC_APROVADAS)].copy()
    manual = df[df["decisao_cenario"].eq(DEC_MANUAL)].copy()
    recusa = df[df["decisao_cenario"].eq(DEC_RECUSA)].copy()

    return {
        "versao": nome,
        "qtd_operacoes": len(df),
        "qtd_aprovados": len(aprov),
        "taxa_aprovacao_automatica_total": len(aprov) / len(df),
        "taxa_analise_manual": len(manual) / len(df),
        "taxa_recusa": len(recusa) / len(df),
        "valor_solicitado_total": df["valor_emprestado"].sum(),
        "valor_aprovado_total": df["valor_aprovado_cenario"].sum(),
        "pct_exposicao_aprovada": df["valor_aprovado_cenario"].sum() / df["valor_emprestado"].sum(),
        "bad_rate_aprovados": aprov["target_inadimplente_12m"].mean() if len(aprov) else np.nan,
        "pd_media_aprovados": aprov["pd_score"].mean() if len(aprov) else np.nan,
        "pd_media_ponderada_valor_aprovado": media_ponderada(aprov, "pd_score", "valor_aprovado_cenario"),
    }

alt = exp.copy()

mask_trava = (
    alt["faixa_risco"].astype(str).str.startswith(("A", "B"))
    & (alt["restritivos_sobre_renda"].fillna(0) > 0.10)
    & alt["decisao_cenario"].isin(DEC_APROVADAS)
)

qtd_trava = int(mask_trava.sum())
valor_trava = float(alt.loc[mask_trava, "valor_aprovado_cenario"].sum())

alt.loc[mask_trava, "decisao_cenario"] = DEC_MANUAL
alt.loc[mask_trava, "valor_aprovado_cenario"] = 0.0

sens = pd.DataFrame([
    resumo_cenario_df(exp, "Expansivo controlado atual"),
    resumo_cenario_df(alt, "Expansivo + trava restritivo severo A/B"),
])

sens["qtd_enviadas_mesa_adicional"] = [0, qtd_trava]
sens["valor_aprovado_reduzido_pela_trava"] = [0, valor_trava]
sens["observacao"] = [
    "Política principal atualmente recomendada.",
    "Teste de sensibilidade: restritivos/renda >10% em A/B vão para análise manual. Não altera política principal automaticamente.",
]

sens.to_csv(
    TABLES / "politica_sensibilidade_trava_restritivo_severo.csv",
    index=False,
    encoding="utf-8-sig",
)

print(sens.to_string(index=False))

# ============================================================
# Resumo para slides
# ============================================================

print("\n7) Gerando politica_resumo_melhorias_v14.md")

manual_exp = exp[exp["decisao_cenario"].eq(DEC_MANUAL)]
qtd_manual_exp = len(manual_exp)
perc_manual_exp = qtd_manual_exp / len(exp)

resumo_md = f"""
# Resumo executivo — melhorias de política v14

## Comprometimento histórico vs teto

A política reduz a alavancagem automática em ratings de maior risco.

- B: comprometimento histórico mediano {comp.loc[comp['faixa_risco'].str.startswith('B'), 'comprometimento_historico_mediano'].iloc[0]:.1%} → teto política {comp.loc[comp['faixa_risco'].str.startswith('B'), 'pct_max_comprometimento_politica'].iloc[0]:.1%}
- C: comprometimento histórico mediano {comp.loc[comp['faixa_risco'].str.startswith('C'), 'comprometimento_historico_mediano'].iloc[0]:.1%} → teto política {comp.loc[comp['faixa_risco'].str.startswith('C'), 'pct_max_comprometimento_politica'].iloc[0]:.1%}
- D: comprometimento histórico mediano {comp.loc[comp['faixa_risco'].str.startswith('D'), 'comprometimento_historico_mediano'].iloc[0]:.1%} → análise manual, sem limite automático

## Mesa operacional

No cenário recomendado, {perc_manual_exp:.2%} da base vai para análise manual, equivalente a {qtd_manual_exp:,} operações no backtest.

## Restritivo severo em A/B

O teste de sensibilidade identifica {qtd_trava:,} operações A/B com restritivo acima de 10% da renda e aprovação automática atual.

Essa trava pode ser avaliada no piloto, mas não altera a política principal nesta versão.
""".strip()

(TABLES / "politica_resumo_melhorias_v14.md").write_text(resumo_md, encoding="utf-8")

print(resumo_md)

print("\n" + "=" * 90)
print("FIM — auditorias complementares geradas com sucesso")
print("=" * 90)