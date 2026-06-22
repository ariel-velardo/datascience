from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path.cwd()
if ROOT.name in {"scripts", "notebooks"}:
    ROOT = ROOT.parent

TABLES = ROOT / "outputs" / "tables"
PROCESSED = ROOT / "data" / "processed"

BASE_SIM = PROCESSED / "base_simulacao_cenarios_politica.parquet"

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

def media_ponderada(df, valor_col, peso_col):
    tmp = df[[valor_col, peso_col]].copy()
    tmp[valor_col] = pd.to_numeric(tmp[valor_col], errors="coerce")
    tmp[peso_col] = pd.to_numeric(tmp[peso_col], errors="coerce")
    tmp = tmp.dropna()
    tmp = tmp[tmp[peso_col] > 0]
    if len(tmp) == 0:
        return np.nan
    return float(np.average(tmp[valor_col], weights=tmp[peso_col]))

def ordenar_rating(df, col="faixa_risco"):
    if col in df.columns:
        df[col] = pd.Categorical(df[col], categories=ORDEM_RATING, ordered=True)
        df = df.sort_values(col)
        df[col] = df[col].astype(str)
    return df

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

print("=" * 90)
print("GERAÇÃO COMPLEMENTAR — RESTRITIVO SEVERO A/B E SENSIBILIDADE V14")
print("=" * 90)

if not BASE_SIM.exists():
    raise FileNotFoundError(f"Base simulada não encontrada: {BASE_SIM}")

base_sim = pd.read_parquet(BASE_SIM)

if "id_operacao" not in base_sim.columns:
    base_sim = base_sim.copy()
    base_sim["id_operacao"] = np.arange(len(base_sim))

if "classe_restritivo_cenario" not in base_sim.columns:
    raise ValueError(
        "Coluna classe_restritivo_cenario ausente. "
        "Sem essa coluna, não é possível identificar restritivo severo pela base simulada."
    )

exp = base_sim[base_sim["cenario"] == CENARIO_RECOMENDADO].copy()

print(f"\nBase do cenário recomendado: {len(exp):,} operações")
print("\nDistribuição da classe de restritivo no cenário recomendado:")
print(exp["classe_restritivo_cenario"].value_counts(dropna=False).to_string())

# ============================================================
# 1. Restritivo severo em A/B
# ============================================================

mask_ab = exp["faixa_risco"].astype(str).str.startswith(("A", "B"))
mask_severo = exp["classe_restritivo_cenario"].eq("acima_10pct")
ab_severo = exp[mask_ab & mask_severo].copy()

restr_ab = (
    ab_severo
    .groupby(["faixa_risco", "classe_restritivo_cenario"], as_index=False)
    .agg(
        qtd_operacoes=("id_operacao", "count"),
        qtd_aprovacao_automatica=("decisao_cenario", lambda s: s.isin(DEC_APROVADAS).sum()),
        valor_solicitado_total=("valor_emprestado", "sum"),
        valor_aprovado_total=("valor_aprovado_cenario", "sum"),
        pd_media=("pd_score", "mean"),
        bad_rate_observado=("target_inadimplente_12m", "mean"),
    )
)

restr_ab["leitura_risco"] = (
    "Grupo A/B com restritivo acima de 10% da renda. "
    "Política atual reduz limite, mas evolução possível é envio à mesa."
)

restr_ab = ordenar_rating(restr_ab)

restr_ab.to_csv(
    TABLES / "politica_restritivo_severo_ab.csv",
    index=False,
    encoding="utf-8-sig",
)

print("\n1) politica_restritivo_severo_ab.csv")
print(restr_ab.to_string(index=False))

# ============================================================
# 2. Sensibilidade: trava restritivo severo A/B
# ============================================================

alt = exp.copy()

mask_trava = (
    alt["faixa_risco"].astype(str).str.startswith(("A", "B"))
    & alt["classe_restritivo_cenario"].eq("acima_10pct")
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
    "Teste de sensibilidade: classe_restritivo_cenario = acima_10pct em A/B vai para análise manual. Não altera política principal automaticamente.",
]

sens.to_csv(
    TABLES / "politica_sensibilidade_trava_restritivo_severo.csv",
    index=False,
    encoding="utf-8-sig",
)

print("\n2) politica_sensibilidade_trava_restritivo_severo.csv")
print(sens.to_string(index=False))

# ============================================================
# 3. Resumo executivo para a v14
# ============================================================

comp_path = TABLES / "politica_comprometimento_historico_vs_teto.csv"
mesa_path = TABLES / "politica_mesa_operacional.csv"

resumo_linhas = []

if comp_path.exists():
    comp = pd.read_csv(comp_path)

    def pegar(prefixo, coluna):
        return comp.loc[comp["faixa_risco"].astype(str).str.startswith(prefixo), coluna].iloc[0]

    resumo_linhas.append("# Resumo executivo — melhorias de política v14")
    resumo_linhas.append("")
    resumo_linhas.append("## Comprometimento histórico vs teto")
    resumo_linhas.append("")
    resumo_linhas.append("A política reduz a alavancagem automática em ratings de maior risco.")
    resumo_linhas.append("")
    resumo_linhas.append(
        f"- B: comprometimento histórico mediano {pegar('B', 'comprometimento_historico_mediano'):.1%} "
        f"→ teto política {pegar('B', 'pct_max_comprometimento_politica'):.1%}"
    )
    resumo_linhas.append(
        f"- C: comprometimento histórico mediano {pegar('C', 'comprometimento_historico_mediano'):.1%} "
        f"→ teto política {pegar('C', 'pct_max_comprometimento_politica'):.1%}"
    )
    resumo_linhas.append(
        f"- D: comprometimento histórico mediano {pegar('D', 'comprometimento_historico_mediano'):.1%} "
        f"→ análise manual, sem limite automático"
    )

if mesa_path.exists():
    mesa = pd.read_csv(mesa_path)
    mesa_exp = mesa[mesa["cenario"].eq(CENARIO_RECOMENDADO)]
    qtd_manual = int(mesa_exp["qtd_manual"].sum())
    qtd_total = len(exp)
    perc_manual = qtd_manual / qtd_total

    resumo_linhas.append("")
    resumo_linhas.append("## Mesa operacional")
    resumo_linhas.append("")
    resumo_linhas.append(
        f"No cenário recomendado, {perc_manual:.2%} da base vai para análise manual, "
        f"equivalente a {qtd_manual:,} operações no backtest."
    )

resumo_linhas.append("")
resumo_linhas.append("## Restritivo severo em A/B")
resumo_linhas.append("")
resumo_linhas.append(
    f"O teste de sensibilidade identifica {qtd_trava:,} operações A/B com restritivo acima de 10% da renda "
    f"e aprovação automática atual."
)
resumo_linhas.append(
    "Essa trava pode ser avaliada no piloto, mas não altera a política principal nesta versão."
)

resumo_md = "\n".join(resumo_linhas)

(TABLES / "politica_resumo_melhorias_v14.md").write_text(resumo_md, encoding="utf-8")

print("\n3) politica_resumo_melhorias_v14.md")
print(resumo_md)

print("\n" + "=" * 90)
print("FIM — geração complementar concluída")
print("=" * 90)