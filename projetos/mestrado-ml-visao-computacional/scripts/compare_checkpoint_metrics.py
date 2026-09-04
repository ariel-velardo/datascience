"""
Compara o checkpoint antigo (selecao por val_loss) com o novo checkpoint
(selecao por val_group_balanced_accuracy) usando predicoes de grupo ja
salvas em validacao e teste.

Objetivo
--------
Nao retreina nenhum modelo e nao recalcula bootstrap. Le:
- reports/tables/baseline_cnn_val_group_predictions.csv (antigo, validacao)
- reports/tables/baseline_cnn_test_group_predictions.csv (antigo, teste)
- reports/tables/baseline_cnn_group_metric_val_group_predictions.csv (novo, validacao)
- reports/tables/baseline_cnn_group_metric_test_group_predictions.csv (novo, teste)
- reports/tables/bootstrap_group_metrics.csv (IC 95% ja calculado por
  scripts/run_bootstrap_ci.py para os model_label correspondentes)

Calcula metricas pontuais (accuracy, balanced accuracy, precisao,
sensibilidade, especificidade, F1, ROC-AUC, average precision, matriz de
confusao) via compute_binary_classification_metrics (reuso, sem
reimplementar nenhuma logica de metrica), junta o IC 95% ja existente, e
monta linhas de delta (novo - antigo) para validacao e teste.

As linhas de delta nao tem IC proprio (nao foi implementado um bootstrap
pareado nesta rodada) - isso fica explicito nas colunas *_ci_lower/*_ci_upper
como NaN, para nao sugerir significancia estatistica que nao foi calculada.

Exemplo de uso
--------------
python scripts/compare_checkpoint_metrics.py
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from liverct.evaluation.classification_metrics import (  # noqa: E402
    compute_binary_classification_metrics,
)

POINT_METRIC_NAMES = [
    "accuracy",
    "balanced_accuracy",
    "precision",
    "recall_sensitivity",
    "specificity",
    "f1",
    "roc_auc",
    "average_precision",
]

CONFUSION_MATRIX_NAMES = ["tn", "fp", "fn", "tp"]


def parse_args() -> argparse.Namespace:
    tables_dir = PROJECT_ROOT / "reports" / "tables"
    parser = argparse.ArgumentParser(
        description=(
            "Compara o checkpoint antigo (val_loss) com o novo checkpoint "
            "(val_group_balanced_accuracy) usando predicoes de grupo ja "
            "salvas. Nao treina nem retreina nenhum modelo."
        ),
    )
    parser.add_argument(
        "--old-val-group-predictions",
        type=Path,
        default=tables_dir / "baseline_cnn_val_group_predictions.csv",
    )
    parser.add_argument(
        "--old-test-group-predictions",
        type=Path,
        default=tables_dir / "baseline_cnn_test_group_predictions.csv",
    )
    parser.add_argument(
        "--new-val-group-predictions",
        type=Path,
        default=tables_dir / "baseline_cnn_group_metric_val_group_predictions.csv",
    )
    parser.add_argument(
        "--new-test-group-predictions",
        type=Path,
        default=tables_dir / "baseline_cnn_group_metric_test_group_predictions.csv",
    )
    parser.add_argument(
        "--bootstrap-csv",
        type=Path,
        default=tables_dir / "bootstrap_group_metrics.csv",
    )
    parser.add_argument("--old-model-label", type=str, default="baseline_cnn")
    parser.add_argument("--new-model-label", type=str, default="baseline_cnn_group_metric")
    parser.add_argument("--threshold", type=float, default=0.5)
    parser.add_argument(
        "--output",
        type=Path,
        default=tables_dir / "baseline_cnn_checkpoint_metric_comparison.csv",
    )
    return parser.parse_args()


def build_model_row(
    path: Path,
    model_label: str,
    split: str,
    threshold: float,
) -> dict[str, Any]:
    """Compute point metrics and confusion matrix for one group predictions file."""
    if not path.exists():
        raise FileNotFoundError(f"Arquivo de predicoes de grupo nao encontrado: {path}")

    df = pd.read_csv(path)
    metrics = compute_binary_classification_metrics(
        y_true=df["label"],
        y_score=df["prob_positive"],
        threshold=threshold,
    )

    row: dict[str, Any] = {
        "row_type": "model",
        "model_label": model_label,
        "split": split,
        "n_groups": len(df),
        "source_file": path.name,
    }
    row.update({name: metrics[name] for name in POINT_METRIC_NAMES})
    row.update({name: metrics[name] for name in CONFUSION_MATRIX_NAMES})
    return row


def attach_bootstrap_ci(row: dict[str, Any], bootstrap_df: pd.DataFrame) -> dict[str, Any]:
    """Attach existing bootstrap CI (from run_bootstrap_ci.py) for one model/split."""
    subset = bootstrap_df[
        (bootstrap_df["model_label"] == row["model_label"])
        & (bootstrap_df["split"] == row["split"])
    ]

    for name in POINT_METRIC_NAMES:
        match = subset[subset["metric"] == name]
        if match.empty:
            print(
                f"[AVISO] IC nao encontrado em bootstrap_group_metrics.csv para "
                f"model_label={row['model_label']!r} split={row['split']!r} metric={name!r}. "
                "Rode scripts/run_bootstrap_ci.py antes de confiar neste IC."
            )
            row[f"{name}_ci_lower"] = float("nan")
            row[f"{name}_ci_upper"] = float("nan")
        else:
            row[f"{name}_ci_lower"] = float(match["ci_lower"].iloc[0])
            row[f"{name}_ci_upper"] = float(match["ci_upper"].iloc[0])

    return row


def build_delta_row(new_row: dict[str, Any], old_row: dict[str, Any], split: str) -> dict[str, Any]:
    """
    Build a delta row (new - old) for one split.

    No paired-bootstrap CI is computed for the delta itself in this round;
    the *_ci_lower/*_ci_upper columns are left as NaN on purpose, so the
    comparison table never implies a significance test that was not run.
    """
    row: dict[str, Any] = {
        "row_type": "delta",
        "model_label": f"{new_row['model_label']}_minus_{old_row['model_label']}",
        "split": split,
        "n_groups": None,
        "source_file": None,
    }
    for name in POINT_METRIC_NAMES + CONFUSION_MATRIX_NAMES:
        row[name] = new_row[name] - old_row[name]
    for name in POINT_METRIC_NAMES:
        row[f"{name}_ci_lower"] = float("nan")
        row[f"{name}_ci_upper"] = float("nan")
    return row


def print_comparison(comparison_df: pd.DataFrame) -> None:
    display_columns = [
        "row_type",
        "model_label",
        "split",
        "n_groups",
        "balanced_accuracy",
        "recall_sensitivity",
        "specificity",
        "f1",
        "roc_auc",
        "average_precision",
        "tn",
        "fp",
        "fn",
        "tp",
    ]
    print("\n=== COMPARACAO CHECKPOINT ANTIGO (val_loss) vs NOVO (val_group_balanced_accuracy) ===")
    print(comparison_df[display_columns].to_string(index=False))


def main() -> None:
    args = parse_args()

    if not args.bootstrap_csv.exists():
        raise FileNotFoundError(
            f"Arquivo de bootstrap nao encontrado: {args.bootstrap_csv}. "
            "Rode scripts/run_bootstrap_ci.py antes deste script."
        )
    bootstrap_df = pd.read_csv(args.bootstrap_csv)

    old_val_row = build_model_row(
        args.old_val_group_predictions, args.old_model_label, "val", args.threshold
    )
    old_test_row = build_model_row(
        args.old_test_group_predictions, args.old_model_label, "test", args.threshold
    )
    new_val_row = build_model_row(
        args.new_val_group_predictions, args.new_model_label, "val", args.threshold
    )
    new_test_row = build_model_row(
        args.new_test_group_predictions, args.new_model_label, "test", args.threshold
    )

    old_val_row = attach_bootstrap_ci(old_val_row, bootstrap_df)
    old_test_row = attach_bootstrap_ci(old_test_row, bootstrap_df)
    new_val_row = attach_bootstrap_ci(new_val_row, bootstrap_df)
    new_test_row = attach_bootstrap_ci(new_test_row, bootstrap_df)

    delta_val_row = build_delta_row(new_val_row, old_val_row, split="val")
    delta_test_row = build_delta_row(new_test_row, old_test_row, split="test")

    comparison_df = pd.DataFrame(
        [old_val_row, new_val_row, delta_val_row, old_test_row, new_test_row, delta_test_row]
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    comparison_df.to_csv(args.output, index=False, encoding="utf-8")

    print_comparison(comparison_df)
    print(f"\nSaida gerada: {args.output}")
    print(
        "\nNota metodologica: as linhas 'delta' nao tem intervalo de confianca "
        "proprio (nenhum bootstrap pareado foi calculado nesta rodada). Use a "
        "sobreposicao dos IC 95% de cada modelo (linhas 'model') como sinal "
        "qualitativo de robustez, nao como teste de significancia formal."
    )


if __name__ == "__main__":
    main()
