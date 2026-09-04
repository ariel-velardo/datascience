"""
Bootstrap por grupo (IC 95%) sobre predicoes de grupo ja salvas.

Objetivo
--------
Nenhuma comparacao ja reportada no projeto (CNN vs. baseline estatistico,
os 3 bracos de ROI, as variantes de MIL) vem hoje com intervalo de
confianca. Este script reamostra com reposicao os grupos (inferred_group_id)
de um arquivo reports/tables/*_group_predictions.csv ja existente e
recalcula as metricas de classificacao binaria a cada reamostra, produzindo
um IC 95% por percentil.

Este script nao treina nem retreina nenhum modelo. Ele so le predicoes ja
salvas.

Exemplo de uso
---------------
python scripts/run_bootstrap_ci.py \
    --input reports/tables/baseline_cnn_test_group_predictions.csv \
    --model-label baseline_cnn

python scripts/run_bootstrap_ci.py \
    --input reports/tables/mil_group_predictions.csv \
    --split-value test --filter-col pooling_mode --filter-value mean_pooling \
    --model-label mil_mean_pooling
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from liverct.evaluation.bootstrap import bootstrap_group_metrics


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Bootstrap por grupo (IC 95%) sobre um arquivo de predicoes de "
            "grupo ja salvo. Nao treina nem retreina modelo."
        ),
    )
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--label-col", type=str, default="label")
    parser.add_argument("--prob-col", type=str, default="prob_positive")
    parser.add_argument("--split-col", type=str, default="split")
    parser.add_argument("--split-value", type=str, default=None)
    parser.add_argument("--filter-col", type=str, default=None)
    parser.add_argument("--filter-value", type=str, default=None)
    parser.add_argument("--threshold", type=float, default=0.5)
    parser.add_argument("--n-bootstrap", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--ci", type=float, default=0.95)
    parser.add_argument("--model-label", type=str, default=None)
    parser.add_argument(
        "--output",
        type=Path,
        default=PROJECT_ROOT / "reports" / "tables" / "bootstrap_group_metrics.csv",
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

    metrics_df = bootstrap_group_metrics(
        df,
        label_col=args.label_col,
        prob_col=args.prob_col,
        threshold=args.threshold,
        n_bootstrap=args.n_bootstrap,
        seed=args.seed,
        ci=args.ci,
    )

    metrics_df.insert(0, "source_file", args.input.name)
    metrics_df.insert(1, "model_label", model_label)
    metrics_df.insert(2, "split", split_label)
    metrics_df.insert(3, "n_groups_input", len(df))

    upsert_output(args.output, metrics_df)

    print("=== BOOTSTRAP POR GRUPO (IC 95%) ===")
    print(f"Entrada: {args.input}")
    print(f"model_label: {model_label} | split: {split_label} | n_grupos: {len(df)}")
    print(f"threshold: {args.threshold} | n_bootstrap: {args.n_bootstrap} | seed: {args.seed}")
    display_columns = ["metric", "point_estimate", "ci_lower", "ci_upper", "n_valid_resamples"]
    print(metrics_df[display_columns].to_string(index=False))
    print(f"\nSaida atualizada: {args.output}")


if __name__ == "__main__":
    main()
