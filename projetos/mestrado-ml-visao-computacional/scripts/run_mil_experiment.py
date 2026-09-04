"""
Executa experimento de Multiple Instance Learning por grupo.

Observacoes metodologicas
-------------------------
- Cada inferred_group_id e tratado como uma bag de slices.
- O script usa o split existente por inferred_group_id.
- O script nao cria, altera ou reamostra splits.
- O conjunto de teste e avaliado apenas apos selecao por validacao.
- O estudo e exploratorio e nao validado clinicamente.
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

from liverct.models.mil_experiment import (  # noqa: E402
    DEFAULT_POOLING_MODES,
    MILExperimentConfig,
    parse_pooling_modes,
    run_mil_experiment,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Train and evaluate group-level MIL models.",
    )
    parser.add_argument(
        "--split-csv",
        type=Path,
        default=PROJECT_ROOT / "data" / "interim" / "split_slices.csv",
    )
    parser.add_argument(
        "--reports-dir",
        type=Path,
        default=PROJECT_ROOT / "reports" / "tables",
    )
    parser.add_argument(
        "--figures-dir",
        type=Path,
        default=PROJECT_ROOT / "reports" / "figures",
    )
    parser.add_argument(
        "--checkpoint-dir",
        type=Path,
        default=PROJECT_ROOT / "models" / "checkpoints" / "mil_experiments",
    )
    parser.add_argument(
        "--pooling",
        nargs="+",
        default=list(DEFAULT_POOLING_MODES),
        choices=list(DEFAULT_POOLING_MODES),
        help="MIL pooling modes to run. Default: all.",
    )
    parser.add_argument("--epochs", type=int, default=10)
    parser.add_argument("--batch-size", type=int, default=1)
    parser.add_argument("--image-size", type=int, default=256)
    parser.add_argument("--max-slices-per-bag", type=int, default=None)
    parser.add_argument("--learning-rate", type=float, default=1e-3)
    parser.add_argument("--weight-decay", type=float, default=1e-4)
    parser.add_argument("--dropout", type=float, default=0.25)
    parser.add_argument("--attention-dim", type=int, default=32)
    parser.add_argument("--patience", type=int, default=4)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--num-workers", type=int, default=0)
    parser.add_argument("--threshold", type=float, default=0.5)
    parser.add_argument(
        "--max-groups-per-split",
        type=int,
        default=None,
        help="Optional reduced group count per split for smoke tests.",
    )
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="Run training/evaluation without writing report tables or figures.",
    )
    return parser.parse_args()


def print_metrics(metrics_df: pd.DataFrame) -> None:
    selected_columns = [
        "model",
        "split",
        "n",
        "balanced_accuracy",
        "sensitivity",
        "specificity",
        "roc_auc",
        "average_precision",
        "precision",
        "recall",
        "f1",
        "tn",
        "fp",
        "fn",
        "tp",
    ]

    print("\n=== MIL GROUP METRICS ===")
    print(metrics_df[selected_columns].to_string(index=False))


def main() -> None:
    args = parse_args()
    config = MILExperimentConfig(
        split_csv_path=args.split_csv,
        reports_dir=args.reports_dir,
        figures_dir=args.figures_dir,
        checkpoint_dir=args.checkpoint_dir,
        pooling_modes=parse_pooling_modes(args.pooling),
        image_size=args.image_size,
        max_slices_per_bag=args.max_slices_per_bag,
        batch_size=args.batch_size,
        epochs=args.epochs,
        learning_rate=args.learning_rate,
        weight_decay=args.weight_decay,
        dropout=args.dropout,
        attention_dim=args.attention_dim,
        patience=args.patience,
        seed=args.seed,
        num_workers=args.num_workers,
        threshold=args.threshold,
        max_groups_per_split=args.max_groups_per_split,
        save_outputs=not args.no_save,
    )

    result = run_mil_experiment(config)
    print_metrics(result["metrics_df"])

    if args.no_save:
        print("\nExecucao sem escrita de tabelas/figuras (--no-save).")
    else:
        print("\nArquivos gerados:")
        for path in result["output_paths"]:
            print(f"  - {path}")


if __name__ == "__main__":
    main()
