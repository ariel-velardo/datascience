from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Sequence

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import torch
from PIL import Image
from torch import nn

from liverct.features.roi_transforms import (
    MaskShape,
    RoiBoxFractions,
    RoiMode,
    build_roi_transform,
    crop_approximate_liver_roi,
    describe_roi_mode,
    mask_approximate_liver_roi,
)
from liverct.models.cnn_dataset import (
    build_dataloader,
    load_split_slices,
    select_split,
    validate_group_split_integrity,
)
from liverct.models.simple_cnn import SimpleCNN2D, count_trainable_parameters
from liverct.models.train_cnn import (
    compute_pos_weight,
    evaluate_loss,
    evaluate_prediction_tables,
    get_device,
    load_cnn_checkpoint,
    predict_with_model,
    set_global_seed,
    train_one_epoch,
)


DEFAULT_APPROACHES: tuple[RoiMode, ...] = (
    "full_image",
    "roi_crop_aproximada",
    "roi_mask_heuristica",
)


@dataclass
class ROIExperimentConfig:
    """Configuration for exploratory ROI classification experiments."""

    split_csv_path: Path
    reports_dir: Path
    checkpoint_dir: Path
    figures_dir: Path
    approaches: tuple[RoiMode, ...] = DEFAULT_APPROACHES
    image_size: int = 256
    batch_size: int = 32
    epochs: int = 20
    learning_rate: float = 1e-3
    weight_decay: float = 1e-4
    dropout: float = 0.25
    patience: int = 5
    seed: int = 42
    num_workers: int = 0
    threshold: float = 0.5
    roi_box: RoiBoxFractions = field(default_factory=RoiBoxFractions)
    mask_shape: MaskShape = "ellipse"
    max_examples: int = 8
    resume_existing: bool = False


def save_roi_checkpoint(
    path: Path,
    model: nn.Module,
    config: ROIExperimentConfig,
    approach: RoiMode,
    epoch: int,
    val_loss: float,
    train_loss: float,
) -> None:
    """Save a checkpoint for one ROI experiment approach."""
    path.parent.mkdir(parents=True, exist_ok=True)
    checkpoint_config = {
        "approach": approach,
        "split_csv_path": str(config.split_csv_path),
        "image_size": config.image_size,
        "batch_size": config.batch_size,
        "epochs": config.epochs,
        "learning_rate": config.learning_rate,
        "weight_decay": config.weight_decay,
        "dropout": config.dropout,
        "patience": config.patience,
        "seed": config.seed,
        "threshold": config.threshold,
        "roi_box": asdict(config.roi_box),
        "mask_shape": config.mask_shape,
    }
    checkpoint = {
        "model_state_dict": model.state_dict(),
        "config": checkpoint_config,
        "epoch": int(epoch),
        "val_loss": float(val_loss),
        "train_loss": float(train_loss),
        "model_name": "SimpleCNN2D",
        "experiment": "roi_hepatica_exploratoria",
    }
    torch.save(checkpoint, path)


def standardize_metric_columns(
    metrics_df: pd.DataFrame,
    approach: RoiMode,
) -> pd.DataFrame:
    """Add approach metadata and metric aliases expected by the ROI comparison."""
    result = metrics_df.copy()
    result.insert(0, "approach", approach)
    result.insert(1, "approach_description", describe_roi_mode(approach))
    result["sensitivity"] = result["recall_sensitivity"]
    result["recall"] = result["recall_sensitivity"]

    ordered_columns = [
        "approach",
        "approach_description",
        "model",
        "level",
        "split",
        "n",
        "threshold",
        "accuracy",
        "balanced_accuracy",
        "precision",
        "recall",
        "sensitivity",
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

    return result[ordered_columns]


def train_one_roi_approach(
    all_df: pd.DataFrame,
    approach: RoiMode,
    config: ROIExperimentConfig,
    device: torch.device,
) -> dict[str, Any]:
    """
    Train and evaluate one ROI approach with the existing group-safe split.

    The test split is evaluated only after model selection by validation loss.
    """
    set_global_seed(config.seed)

    train_df = select_split(all_df, "train")
    val_df = select_split(all_df, "val")
    test_df = select_split(all_df, "test")

    image_transform = build_roi_transform(
        mode=approach,
        roi_box=config.roi_box,
        mask_shape=config.mask_shape,
    )

    train_loader = build_dataloader(
        train_df,
        batch_size=config.batch_size,
        image_size=config.image_size,
        shuffle=True,
        num_workers=config.num_workers,
        image_transform=image_transform,
    )
    val_loader = build_dataloader(
        val_df,
        batch_size=config.batch_size,
        image_size=config.image_size,
        shuffle=False,
        num_workers=config.num_workers,
        image_transform=image_transform,
    )

    model = SimpleCNN2D(dropout=config.dropout).to(device)
    pos_weight = compute_pos_weight(train_df)
    if pos_weight is not None:
        pos_weight = pos_weight.to(device)

    criterion = nn.BCEWithLogitsLoss(pos_weight=pos_weight)
    optimizer = torch.optim.Adam(
        model.parameters(),
        lr=config.learning_rate,
        weight_decay=config.weight_decay,
    )

    best_val_loss = float("inf")
    best_epoch = 0
    epochs_without_improvement = 0
    history_rows: list[dict[str, float | int | str]] = []
    checkpoint_path = config.checkpoint_dir / f"{approach}_best.pt"

    print(f"\n=== ROI approach: {approach} ===")
    print(f"Description: {describe_roi_mode(approach)}")
    print(f"Train slices: {len(train_df)} | Val slices: {len(val_df)}")
    print(f"Trainable parameters: {count_trainable_parameters(model)}")

    for epoch in range(1, config.epochs + 1):
        train_loss = train_one_epoch(
            model=model,
            dataloader=train_loader,
            criterion=criterion,
            optimizer=optimizer,
            device=device,
        )
        val_loss = evaluate_loss(
            model=model,
            dataloader=val_loader,
            criterion=criterion,
            device=device,
        )

        improved = val_loss < best_val_loss
        if improved:
            best_val_loss = val_loss
            best_epoch = epoch
            epochs_without_improvement = 0
            save_roi_checkpoint(
                path=checkpoint_path,
                model=model,
                config=config,
                approach=approach,
                epoch=epoch,
                val_loss=val_loss,
                train_loss=train_loss,
            )
        else:
            epochs_without_improvement += 1

        history_rows.append(
            {
                "approach": approach,
                "epoch": epoch,
                "train_loss": train_loss,
                "val_loss": val_loss,
                "best_val_loss": best_val_loss,
                "best_epoch": best_epoch,
                "improved": int(improved),
            }
        )

        print(
            f"Epoch {epoch:03d}/{config.epochs} | "
            f"train_loss={train_loss:.5f} | "
            f"val_loss={val_loss:.5f} | "
            f"best_epoch={best_epoch}"
        )

        if epochs_without_improvement >= config.patience:
            print(f"Early stopping at epoch {epoch}.")
            break

    best_model, checkpoint = load_cnn_checkpoint(checkpoint_path, device=device)

    prediction_outputs = []
    metric_frames = []
    output_paths: list[Path] = [checkpoint_path]

    for split_name, split_df in [("val", val_df), ("test", test_df)]:
        split_loader = build_dataloader(
            split_df,
            batch_size=config.batch_size,
            image_size=config.image_size,
            shuffle=False,
            num_workers=config.num_workers,
            image_transform=image_transform,
        )

        slice_pred_df = predict_with_model(
            model=best_model,
            dataloader=split_loader,
            device=device,
            threshold=config.threshold,
        )
        slice_pred_df, group_pred_df, metrics_df = evaluate_prediction_tables(
            slice_pred_df,
            threshold=config.threshold,
        )

        slice_pred_df.insert(0, "approach", approach)
        group_pred_df.insert(0, "approach", approach)
        metrics_df = standardize_metric_columns(metrics_df, approach=approach)

        slice_pred_path = config.reports_dir / (
            f"roi_{approach}_{split_name}_slice_predictions.csv"
        )
        group_pred_path = config.reports_dir / (
            f"roi_{approach}_{split_name}_group_predictions.csv"
        )
        metrics_path = config.reports_dir / f"roi_{approach}_{split_name}_metrics.csv"

        slice_pred_df.to_csv(slice_pred_path, index=False, encoding="utf-8")
        group_pred_df.to_csv(group_pred_path, index=False, encoding="utf-8")
        metrics_df.to_csv(metrics_path, index=False, encoding="utf-8")

        output_paths.extend([slice_pred_path, group_pred_path, metrics_path])
        metric_frames.append(metrics_df)
        prediction_outputs.append(
            {
                "split": split_name,
                "slice_predictions": slice_pred_df,
                "group_predictions": group_pred_df,
                "metrics": metrics_df,
            }
        )

    history_df = pd.DataFrame(history_rows)
    history_path = config.reports_dir / f"roi_{approach}_training_history.csv"
    history_df.to_csv(history_path, index=False, encoding="utf-8")
    output_paths.append(history_path)

    return {
        "approach": approach,
        "checkpoint": checkpoint,
        "checkpoint_path": checkpoint_path,
        "history_df": history_df,
        "metrics_df": pd.concat(metric_frames, ignore_index=True),
        "prediction_outputs": prediction_outputs,
        "output_paths": output_paths,
    }


def roi_metric_paths(config: ROIExperimentConfig, approach: RoiMode) -> list[Path]:
    """Return expected metric paths for one approach."""
    return [
        config.reports_dir / f"roi_{approach}_val_metrics.csv",
        config.reports_dir / f"roi_{approach}_test_metrics.csv",
    ]


def can_resume_roi_approach(config: ROIExperimentConfig, approach: RoiMode) -> bool:
    """Check whether saved metrics are available for one approach."""
    return all(path.exists() for path in roi_metric_paths(config, approach))


def load_existing_roi_approach(
    config: ROIExperimentConfig,
    approach: RoiMode,
) -> dict[str, Any]:
    """Load previously saved metrics for an approach."""
    metric_paths = roi_metric_paths(config, approach)
    metrics_df = pd.concat(
        [pd.read_csv(path) for path in metric_paths],
        ignore_index=True,
    )

    history_path = config.reports_dir / f"roi_{approach}_training_history.csv"
    history_df = (
        pd.read_csv(history_path)
        if history_path.exists()
        else pd.DataFrame(columns=["approach", "epoch", "train_loss", "val_loss"])
    )
    checkpoint_path = config.checkpoint_dir / f"{approach}_best.pt"

    output_paths = [
        checkpoint_path,
        history_path,
        *metric_paths,
        config.reports_dir / f"roi_{approach}_val_slice_predictions.csv",
        config.reports_dir / f"roi_{approach}_val_group_predictions.csv",
        config.reports_dir / f"roi_{approach}_test_slice_predictions.csv",
        config.reports_dir / f"roi_{approach}_test_group_predictions.csv",
    ]

    return {
        "approach": approach,
        "checkpoint": None,
        "checkpoint_path": checkpoint_path,
        "history_df": history_df,
        "metrics_df": metrics_df,
        "prediction_outputs": [],
        "output_paths": [path for path in output_paths if path.exists()],
    }


def save_roi_examples(
    df: pd.DataFrame,
    output_dir: Path,
    roi_box: RoiBoxFractions,
    mask_shape: MaskShape = "ellipse",
    max_examples: int = 8,
    seed: int = 42,
) -> list[Path]:
    """
    Save visual examples comparing full image, approximate crop, and mask.

    Examples are sampled at group level to avoid showing only adjacent slices
    from the same inferred group.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    if max_examples <= 0:
        return []

    base_df = df[df["split"] == "test"].copy()
    if base_df.empty:
        base_df = df.copy()

    sort_columns = [
        column
        for column in ["label", "inferred_group_id", "slice_id", "filename"]
        if column in base_df.columns
    ]
    representative_df = (
        base_df.sort_values(sort_columns)
        .groupby(["label", "inferred_group_id"], as_index=False)
        .first()
    )

    if representative_df.empty:
        return []

    n_examples = min(max_examples, len(representative_df))
    sample_df = sample_examples_by_label(
        representative_df,
        n_examples=n_examples,
        seed=seed,
    )
    sample_df = sample_df.sort_values(["label", "inferred_group_id"]).reset_index(drop=True)

    generated_paths: list[Path] = []

    for idx, row in sample_df.iterrows():
        image_path = Path(str(row["file_path"]))
        if not image_path.exists():
            print(f"[AVISO] imagem nao encontrada para exemplo ROI: {image_path}")
            continue

        output_path = output_dir / make_roi_example_filename(idx, row)

        try:
            plot_roi_example(row, output_path, roi_box=roi_box, mask_shape=mask_shape)
        except OSError as exc:
            print(f"[AVISO] nao foi possivel gerar exemplo ROI para {image_path}: {exc}")
            continue

        generated_paths.append(output_path)

    return generated_paths


def sample_examples_by_label(
    representative_df: pd.DataFrame,
    n_examples: int,
    seed: int,
) -> pd.DataFrame:
    """Sample visual examples with label balance when both classes are present."""
    labels = sorted(representative_df["label"].dropna().unique())
    if not labels:
        return representative_df.head(0)

    per_label = max(1, n_examples // len(labels))
    remainder = n_examples % len(labels)
    selected_indices: list[int] = []

    for label_idx, label in enumerate(labels):
        label_df = representative_df[representative_df["label"] == label]
        target_n = per_label + int(label_idx < remainder)
        target_n = min(target_n, len(label_df))
        if target_n <= 0:
            continue
        selected = label_df.sample(n=target_n, random_state=seed + int(label_idx))
        selected_indices.extend(selected.index.tolist())

    if len(selected_indices) < n_examples:
        remaining_df = representative_df.drop(index=selected_indices)
        if not remaining_df.empty:
            extra_n = min(n_examples - len(selected_indices), len(remaining_df))
            extra = remaining_df.sample(n=extra_n, random_state=seed + 97)
            selected_indices.extend(extra.index.tolist())

    return representative_df.loc[selected_indices]


def make_roi_example_filename(index: int, row: pd.Series) -> str:
    """Build a stable filename for one ROI example figure."""
    group_id = sanitize_filename(str(row["inferred_group_id"]))
    class_name = sanitize_filename(str(row.get("class_name", row["label"])))
    image_stem = sanitize_filename(Path(str(row["file_path"])).stem)
    return f"roi_example_{index:02d}_{class_name}_{group_id}_{image_stem}.png"


def sanitize_filename(value: str) -> str:
    """Keep filenames stable without depending on external path details."""
    return "".join(char if char.isalnum() or char in "-_" else "_" for char in value)


def plot_roi_example(
    row: pd.Series,
    output_path: Path,
    roi_box: RoiBoxFractions,
    mask_shape: MaskShape = "ellipse",
) -> None:
    """Plot full image, approximate crop, and heuristic mask for one slice."""
    image_path = Path(str(row["file_path"]))

    with Image.open(image_path) as image:
        image = image.convert("L")
        full = image.copy()
        crop = crop_approximate_liver_roi(image, roi_box=roi_box)
        mask = mask_approximate_liver_roi(
            image,
            roi_box=roi_box,
            mask_shape=mask_shape,
        )

    box = roi_box.to_pixel_box(full.size)
    label_text = str(row.get("class_name", row.get("label", "")))
    group_id = str(row["inferred_group_id"])
    filename = Path(str(row["file_path"])).name

    fig, axes = plt.subplots(1, 3, figsize=(10, 3.5))

    axes[0].imshow(full, cmap="gray")
    axes[0].set_title("full_image")
    axes[0].axis("off")
    rect = plt.Rectangle(
        (box[0], box[1]),
        box[2] - box[0],
        box[3] - box[1],
        fill=False,
        edgecolor="tab:red",
        linewidth=1.5,
    )
    axes[0].add_patch(rect)

    axes[1].imshow(crop, cmap="gray")
    axes[1].set_title("roi_crop_aproximada")
    axes[1].axis("off")

    axes[2].imshow(mask, cmap="gray")
    axes[2].set_title("roi_mask_heuristica")
    axes[2].axis("off")

    fig.suptitle(
        f"{label_text} | {group_id} | {filename}\n"
        "ROI heuristica, exploratoria e nao clinica",
        fontsize=10,
    )
    fig.tight_layout()
    fig.savefig(output_path, dpi=160, bbox_inches="tight")
    plt.close(fig)


def run_roi_experiments(config: ROIExperimentConfig) -> dict[str, Any]:
    """
    Run all configured ROI approaches and save comparison artifacts.

    This function reads existing split assignments and never creates or modifies
    train/validation/test splits.
    """
    config.reports_dir.mkdir(parents=True, exist_ok=True)
    config.checkpoint_dir.mkdir(parents=True, exist_ok=True)
    config.figures_dir.mkdir(parents=True, exist_ok=True)
    config.roi_box.validate()

    all_df = load_split_slices(config.split_csv_path)
    validate_group_split_integrity(all_df)

    device = get_device()
    print(f"Device: {device}")
    print(f"Split file: {config.split_csv_path}")
    print(f"ROI box: {asdict(config.roi_box)} | mask_shape={config.mask_shape}")

    example_paths = save_roi_examples(
        df=all_df,
        output_dir=config.figures_dir / "roi_examples",
        roi_box=config.roi_box,
        mask_shape=config.mask_shape,
        max_examples=config.max_examples,
        seed=config.seed,
    )

    approach_results = []
    metric_frames = []
    output_paths: list[Path] = []

    for approach in config.approaches:
        if config.resume_existing and can_resume_roi_approach(config, approach):
            print(f"\n=== ROI approach: {approach} ===")
            print("Metricas existentes encontradas; pulando treino.")
            result = load_existing_roi_approach(config=config, approach=approach)
        else:
            result = train_one_roi_approach(
                all_df=all_df,
                approach=approach,
                config=config,
                device=device,
            )
        approach_results.append(result)
        metric_frames.append(result["metrics_df"])
        output_paths.extend(result["output_paths"])

    comparison_df = pd.concat(metric_frames, ignore_index=True)
    comparison_path = config.reports_dir / "roi_experiment_comparison.csv"
    comparison_df.to_csv(comparison_path, index=False, encoding="utf-8")

    history_df = pd.concat(
        [result["history_df"] for result in approach_results],
        ignore_index=True,
    )
    history_path = config.reports_dir / "roi_experiment_training_history.csv"
    history_df.to_csv(history_path, index=False, encoding="utf-8")

    output_paths.extend([comparison_path, history_path, *example_paths])

    return {
        "comparison_df": comparison_df,
        "history_df": history_df,
        "example_paths": example_paths,
        "approach_results": approach_results,
        "output_paths": output_paths,
    }


def parse_approaches(values: Sequence[str]) -> tuple[RoiMode, ...]:
    """Validate CLI approach names."""
    valid = set(DEFAULT_APPROACHES)
    approaches: list[RoiMode] = []
    for value in values:
        if value not in valid:
            raise ValueError(f"Invalid approach: {value}. Valid values: {sorted(valid)}")
        approaches.append(value)  # type: ignore[arg-type]
    return tuple(approaches)
