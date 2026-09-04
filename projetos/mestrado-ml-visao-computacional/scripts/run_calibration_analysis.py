"""
Calibracao simples (Brier score + reliability curve) sobre predicoes de
grupo ja salvas.

Objetivo
--------
O projeto nao tem nenhum codigo de calibracao de probabilidade (achado
MET-03 da auditoria). Como as probabilidades de grupo ja sao usadas para
ordenar casos (analise de erro, selecao de casos para Grad-CAM), este script
calcula o Brier score e uma reliability table/curve (probabilidade prevista
vs. frequencia observada, por bins) em nivel de grupo, sobre predicoes ja
salvas.

Este script nao treina nem retreina nenhum modelo, e nao implementa
temperature scaling (fica registrado como proximo passo natural, nao
implementado nesta rodada). Nenhum resultado aqui deve ser lido como
validacao clinica.

Exemplo de uso
---------------
python scripts/run_calibration_analysis.py \
    --input reports/tables/baseline_cnn_test_group_predictions.csv \
    --model-label baseline_cnn
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from liverct.evaluation.calibration import compute_brier_score, compute_reliability_table


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Brier score e reliability table/curve de grupo sobre um arquivo "
            "de predicoes ja salvo. Nao treina nem retreina modelo."
        ),
    )
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--label-col", type=str, default="label")
    parser.add_argument("--prob-col", type=str, default="prob_positive")
    parser.add_argument("--split-col", type=str, default="split")
    parser.add_argument("--split-value", type=str, default=None)
    parser.add_argument("--filter-col", type=str, default=None)
    parser.add_argument("--filter-value", type=str, default=None)
    parser.add_argument("--n-bins", type=int, default=5)
    parser.add_argument("--model-label", type=str, default=None)
    parser.add_argument(
        "--output",
        type=Path,
        default=PROJECT_ROOT / "reports" / "tables" / "calibration_group_metrics.csv",
    )
    parser.add_argument(
        "--figure-dir",
        type=Path,
        default=PROJECT_ROOT / "reports" / "figures" / "calibration",
    )
    return parser.parse_args()


def apply_filters(
    df: pd.DataFrame,
    split_col: str,
    split_value: str | None,
    filter_col: str | None,
    filter_value: str | None,
) -> pd.DataFrame:
    filtered = df

    if filter_col is not None:
        if filter_col not in filtered.columns:
            raise ValueError(f"Coluna de filtro nao encontrada: {filter_col}")
        filtered = filtered[filtered[filter_col].astype(str) == str(filter_value)]

    if split_value is not None:
        if split_col not in filtered.columns:
            raise ValueError(f"Coluna de split nao encontrada: {split_col}")
        filtered = filtered[filtered[split_col].astype(str) == str(split_value)]

    return filtered.reset_index(drop=True)


def resolve_split_label(df: pd.DataFrame, split_col: str, split_value: str | None) -> str:
    if split_value is not None:
        return split_value
    if split_col in df.columns:
        unique_values = df[split_col].astype(str).unique().tolist()
        if len(unique_values) == 1:
            return unique_values[0]
        return "mixed"
    return "unknown"


def upsert_output(output_path: Path, new_rows: pd.DataFrame) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if output_path.exists():
        existing = pd.read_csv(output_path)
        key_columns = ["source_file", "model_label", "split"]
        mask = existing[key_columns].apply(tuple, axis=1).isin(
            new_rows[key_columns].apply(tuple, axis=1)
        )
        existing = existing[~mask]
        combined = pd.concat([existing, new_rows], ignore_index=True)
    else:
        combined = new_rows

    combined.to_csv(output_path, index=False, encoding="utf-8")


def plot_reliability_curve(
    reliability_df: pd.DataFrame,
    brier_score: float,
    model_label: str,
    split_label: str,
    output_path: Path,
) -> None:
    fig, ax = plt.subplots(figsize=(5, 5))

    ax.plot([0, 1], [0, 1], linestyle="--", color="gray", label="Calibracao perfeita")

    valid = reliability_df.dropna(subset=["mean_predicted", "empirical_frequency"])
    ax.plot(
        valid["mean_predicted"],
        valid["empirical_frequency"],
        marker="o",
        color="tab:blue",
        label="Observado (por bin)",
    )
    for _, row in valid.iterrows():
        ax.annotate(f"n={int(row['n'])}", (row["mean_predicted"], row["empirical_frequency"]))

    ax.set_xlim(-0.02, 1.02)
    ax.set_ylim(-0.02, 1.02)
    ax.set_xlabel("Probabilidade prevista (media por bin)")
    ax.set_ylabel("Frequencia observada (por bin)")
    ax.set_title(f"{model_label} | {split_label} | Brier={brier_score:.4f}")
    ax.legend(loc="upper left", fontsize=8)

    fig.tight_layout()
    fig.savefig(output_path, dpi=160, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    args = parse_args()

    if not args.input.exists():
        raise FileNotFoundError(f"Arquivo de entrada nao encontrado: {args.input}")

    df = pd.read_csv(args.input)
    df = apply_filters(
        df,
        split_col=args.split_col,
        split_value=args.split_value,
        filter_col=args.filter_col,
        filter_value=args.filter_value,
    )

    if df.empty:
        raise ValueError(
            "Nenhuma linha restante apos os filtros aplicados. "
            "Verifique --split-value e --filter-col/--filter-value."
        )

    model_label = args.model_label or args.input.stem
    split_label = resolve_split_label(df, args.split_col, args.split_value)

    y_true = df[args.label_col]
    y_prob = df[args.prob_col]

    brier = compute_brier_score(y_true, y_prob)
    reliability_df = compute_reliability_table(y_true, y_prob, n_bins=args.n_bins)

    output_rows = reliability_df.copy()
    output_rows.insert(0, "source_file", args.input.name)
    output_rows.insert(1, "model_label", model_label)
    output_rows.insert(2, "split", split_label)
    output_rows.insert(3, "n_groups_input", len(df))
    output_rows.insert(4, "brier_score", brier)

    upsert_output(args.output, output_rows)

    args.figure_dir.mkdir(parents=True, exist_ok=True)
    figure_path = args.figure_dir / f"{model_label}_{split_label}_reliability.png"
    plot_reliability_curve(reliability_df, brier, model_label, split_label, figure_path)

    print("=== CALIBRACAO DE GRUPO (Brier + reliability) ===")
    print(f"Entrada: {args.input}")
    print(f"model_label: {model_label} | split: {split_label} | n_grupos: {len(df)}")
    print(f"Brier score: {brier:.4f}")
    print(reliability_df.to_string(index=False))
    print(f"\nSaida (tabela) atualizada: {args.output}")
    print(f"Figura salva em: {figure_path}")


if __name__ == "__main__":
    main()
