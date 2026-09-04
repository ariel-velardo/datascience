"""
Executa experimentos exploratorios com ROI hepatica aproximada.

Objetivo
--------
Comparar a CNN 2D usando:
- imagem inteira;
- recorte aproximado da regiao hepatica;
- mascara heuristica aproximada.

Observacoes metodologicas
-------------------------
- O script usa o split existente por inferred_group_id.
- O script nao cria nem modifica splits.
- O conjunto de teste e usado apenas apos selecao por validacao.
- A ROI e heuristica, exploratoria e nao clinica.
- Nenhuma mascara clinica e inventada nesta etapa.
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

from liverct.features.roi_transforms import RoiBoxFractions  # noqa: E402
from liverct.models.roi_experiments import (  # noqa: E402
    DEFAULT_APPROACHES,
    ROIExperimentConfig,
    parse_approaches,
    run_roi_experiments,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Train and compare exploratory CNN ROI approaches.",
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
        default=PROJECT_ROOT / "models" / "checkpoints" / "roi_experiments",
    )
    parser.add_argument(
        "--approaches",
        nargs="+",
        default=list(DEFAULT_APPROACHES),
        choices=list(DEFAULT_APPROACHES),
        help="Approaches to run. Default: all.",
    )
    parser.add_argument("--epochs", type=int, default=20)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--image-size", type=int, default=256)
    parser.add_argument("--learning-rate", type=float, default=1e-3)
    parser.add_argument("--weight-decay", type=float, default=1e-4)
    parser.add_argument("--dropout", type=float, default=0.25)
    parser.add_argument("--patience", type=int, default=5)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--num-workers", type=int, default=0)
    parser.add_argument("--threshold", type=float, default=0.5)
    parser.add_argument("--roi-center-x", type=float, default=0.44)
    parser.add_argument("--roi-center-y", type=float, default=0.53)
    parser.add_argument("--roi-width", type=float, default=0.68)
    parser.add_argument("--roi-height", type=float, default=0.70)
    parser.add_argument(
        "--mask-shape",
        choices=["ellipse", "rectangle"],
        default="ellipse",
    )
    parser.add_argument(
        "--max-examples",
        type=int,
        default=8,
        help="Maximum ROI visual examples to save. Use 0 to skip.",
    )
    parser.add_argument(
        "--resume-existing",
        action="store_true",
        help="Reuse existing per-approach ROI metrics and train only missing approaches.",
    )
    return parser.parse_args()


def print_comparison(metrics_df: pd.DataFrame) -> None:
    selected_columns = [
        "approach",
        "level",
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
    ]

    print("\n=== ROI EXPERIMENT COMPARISON ===")
    print(metrics_df[selected_columns].to_string(index=False))


def main() -> None:
    args = parse_args()

    roi_box = RoiBoxFractions(
        center_x=args.roi_center_x,
        center_y=args.roi_center_y,
        width=args.roi_width,
        height=args.roi_height,
    )

    config = ROIExperimentConfig(
        split_csv_path=args.split_csv,
        reports_dir=args.reports_dir,
        checkpoint_dir=args.checkpoint_dir,
        figures_dir=args.figures_dir,
        approaches=parse_approaches(args.approaches),
        image_size=args.image_size,
        batch_size=args.batch_size,
        epochs=args.epochs,
        learning_rate=args.learning_rate,
        weight_decay=args.weight_decay,
        dropout=args.dropout,
        patience=args.patience,
        seed=args.seed,
        num_workers=args.num_workers,
        threshold=args.threshold,
        roi_box=roi_box,
        mask_shape=args.mask_shape,
        max_examples=args.max_examples,
        resume_existing=args.resume_existing,
    )

    result = run_roi_experiments(config)
    print_comparison(result["comparison_df"])

    print("\nArquivos gerados:")
    for path in result["output_paths"]:
        print(f"  - {path}")


if __name__ == "__main__":
    main()
