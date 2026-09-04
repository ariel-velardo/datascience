from __future__ import annotations

import copy
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Sequence

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import torch
from torch import nn

from liverct.evaluation.classification_metrics import evaluate_predictions_by_split
from liverct.models.mil_dataset import (
    build_mil_dataloader,
    filter_groups_for_smoke_test,
    load_group_safe_split,
    summarize_bags,
)
from liverct.models.mil_model import (
    DEFAULT_POOLING_MODES,
    MILClassifier,
    PoolingMode,
    count_trainable_parameters,
)
from liverct.models.train_cnn import get_device, set_global_seed


@dataclass
class MILExperimentConfig:
    """Configuration for group-level MIL experiments."""

    split_csv_path: Path
    reports_dir: Path
    figures_dir: Path
    checkpoint_dir: Path
    pooling_modes: tuple[PoolingMode, ...] = DEFAULT_POOLING_MODES
    image_size: int = 256
    max_slices_per_bag: int | None = None
    batch_size: int = 1
    epochs: int = 10
    learning_rate: float = 1e-3
    weight_decay: float = 1e-4
    dropout: float = 0.25
    attention_dim: int = 32
    patience: int = 4
    seed: int = 42
    num_workers: int = 0
    threshold: float = 0.5
    max_groups_per_split: int | None = None
    save_outputs: bool = True


def parse_pooling_modes(values: Sequence[str]) -> tuple[PoolingMode, ...]:
    """Validate pooling mode names from CLI or notebooks."""
    valid = set(DEFAULT_POOLING_MODES)
    modes: list[PoolingMode] = []
    for value in values:
        if value not in valid:
            raise ValueError(f"Invalid pooling mode: {value}. Valid values: {sorted(valid)}")
        modes.append(value)  # type: ignore[arg-type]
    return tuple(modes)


def compute_group_pos_weight(df: pd.DataFrame) -> torch.Tensor | None:
    """Compute BCE pos_weight from train groups only."""
    train_groups = (
        df[df["split"] == "train"]
        .groupby("inferred_group_id")
        .agg(label=("label", "first"))
        .reset_index()
    )
    positives = int((train_groups["label"] == 1).sum())
    negatives = int((train_groups["label"] == 0).sum())

    if positives == 0 or negatives == 0:
        return None

    return torch.tensor([negatives / positives], dtype=torch.float32)


def train_one_epoch(
    model: MILClassifier,
    dataloader: torch.utils.data.DataLoader,
    criterion: nn.Module,
    optimizer: torch.optim.Optimizer,
    device: torch.device,
) -> float:
    """Train one epoch over group-level bags."""
    model.train()
    total_loss = 0.0
    total_bags = 0

    for batch in dataloader:
        optimizer.zero_grad(set_to_none=True)
        losses = []

        for bag_images, label in zip(batch["images"], batch["label"]):
            bag_images = bag_images.to(device)
            label = label.to(device).view(1)
            logit = model(bag_images).view(1)
            losses.append(criterion(logit, label))

        loss = torch.stack(losses).mean()
        loss.backward()
        optimizer.step()

        batch_size = len(losses)
        total_loss += float(loss.item()) * batch_size
        total_bags += batch_size

    return total_loss / max(total_bags, 1)


@torch.no_grad()
def evaluate_loss(
    model: MILClassifier,
    dataloader: torch.utils.data.DataLoader,
    criterion: nn.Module,
    device: torch.device,
) -> float:
    """Evaluate mean loss over group-level bags."""
    model.eval()
    total_loss = 0.0
    total_bags = 0

    for batch in dataloader:
        losses = []
        for bag_images, label in zip(batch["images"], batch["label"]):
            bag_images = bag_images.to(device)
            label = label.to(device).view(1)
            logit = model(bag_images).view(1)
            losses.append(criterion(logit, label))

        batch_loss = torch.stack(losses).mean()
        batch_size = len(losses)
        total_loss += float(batch_loss.item()) * batch_size
        total_bags += batch_size

    return total_loss / max(total_bags, 1)


@torch.no_grad()
def predict_groups(
    model: MILClassifier,
    dataloader: torch.utils.data.DataLoader,
    device: torch.device,
    pooling_mode: PoolingMode,
    threshold: float = 0.5,
) -> pd.DataFrame:
    """Generate one prediction per inferred group."""
    model.eval()
    rows: list[dict[str, Any]] = []

    for batch in dataloader:
        for index, bag_images in enumerate(batch["images"]):
            bag_images = bag_images.to(device)
            logit, attention_weights = model(bag_images, return_attention=True)
            prob_positive = float(torch.sigmoid(logit).detach().cpu().item())
            label = int(batch["label"][index].detach().cpu().item())

            row: dict[str, Any] = {
                "model": f"mil_{pooling_mode}",
                "pooling_mode": pooling_mode,
                "split": batch["split"][index],
                "inferred_group_id": batch["inferred_group_id"][index],
                "class_name": batch["class_name"][index],
                "label": label,
                "prob_positive": prob_positive,
                "pred_label": int(prob_positive >= threshold),
                "n_slices": int(batch["n_slices"][index]),
                "n_available_slices": int(batch["n_available_slices"][index]),
            }

            if attention_weights is not None:
                weights = attention_weights.detach().cpu()
                top_idx = int(torch.argmax(weights).item())
                row["top_attention_weight"] = float(weights[top_idx].item())
                row["top_attention_filename"] = batch["filenames"][index][top_idx]
                row["top_attention_slice_id"] = batch["slice_ids"][index][top_idx]
            else:
                row["top_attention_weight"] = None
                row["top_attention_filename"] = None
                row["top_attention_slice_id"] = None

            rows.append(row)

    return pd.DataFrame(rows)


def evaluate_group_predictions(
    predictions_df: pd.DataFrame,
    threshold: float,
) -> pd.DataFrame:
    """Compute metrics by split and pooling mode."""
    metric_frames = []

    for pooling_mode, pooling_df in predictions_df.groupby("pooling_mode", sort=True):
        metrics_df = evaluate_predictions_by_split(
            pooling_df,
            level="group",
            threshold=threshold,
        )
        metrics_df.insert(0, "model", f"mil_{pooling_mode}")
        metrics_df.insert(1, "pooling_mode", pooling_mode)
        metrics_df["sensitivity"] = metrics_df["recall_sensitivity"]
        metrics_df["recall"] = metrics_df["recall_sensitivity"]
        metric_frames.append(metrics_df)

    output = pd.concat(metric_frames, ignore_index=True)
    ordered_columns = [
        "model",
        "pooling_mode",
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
    return output[ordered_columns]


def save_mil_checkpoint(
    path: Path,
    model: MILClassifier,
    config: MILExperimentConfig,
    pooling_mode: PoolingMode,
    epoch: int,
    val_loss: float,
    train_loss: float,
) -> None:
    """Save one MIL checkpoint. Checkpoints are ignored by Git."""
    path.parent.mkdir(parents=True, exist_ok=True)
    checkpoint = {
        "model_state_dict": model.state_dict(),
        "config": {
            **{key: str(value) for key, value in asdict(config).items()},
            "pooling_mode": pooling_mode,
        },
        "epoch": int(epoch),
        "val_loss": float(val_loss),
        "train_loss": float(train_loss),
        "model_name": "MILClassifier",
    }
    torch.save(checkpoint, path)


def train_one_pooling_mode(
    all_df: pd.DataFrame,
    pooling_mode: PoolingMode,
    config: MILExperimentConfig,
    device: torch.device,
) -> dict[str, Any]:
    """Train and evaluate one MIL pooling mode."""
    set_global_seed(config.seed)

    train_loader = build_mil_dataloader(
        all_df,
        split="train",
        image_size=config.image_size,
        max_slices_per_bag=config.max_slices_per_bag,
        batch_size=config.batch_size,
        shuffle=True,
        num_workers=config.num_workers,
    )
    val_loader = build_mil_dataloader(
        all_df,
        split="val",
        image_size=config.image_size,
        max_slices_per_bag=config.max_slices_per_bag,
        batch_size=config.batch_size,
        shuffle=False,
        num_workers=config.num_workers,
    )

    model = MILClassifier(
        pooling_mode=pooling_mode,
        dropout=config.dropout,
        attention_dim=config.attention_dim,
    ).to(device)
    pos_weight = compute_group_pos_weight(all_df)
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
    best_state_dict = copy.deepcopy(model.state_dict())
    epochs_without_improvement = 0
    history_rows: list[dict[str, Any]] = []
    checkpoint_path = config.checkpoint_dir / f"mil_{pooling_mode}_best.pt"

    print(f"\n=== MIL pooling: {pooling_mode} ===")
    print(f"Train bags: {len(train_loader.dataset)} | Val bags: {len(val_loader.dataset)}")
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
            best_state_dict = copy.deepcopy(model.state_dict())
            epochs_without_improvement = 0
            save_mil_checkpoint(
                path=checkpoint_path,
                model=model,
                config=config,
                pooling_mode=pooling_mode,
                epoch=epoch,
                val_loss=val_loss,
                train_loss=train_loss,
            )
        else:
            epochs_without_improvement += 1

        history_rows.append(
            {
                "pooling_mode": pooling_mode,
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

    model.load_state_dict(best_state_dict)
    model.eval()

    prediction_frames = []
    for split_name in ["train", "val", "test"]:
        dataloader = build_mil_dataloader(
            all_df,
            split=split_name,  # type: ignore[arg-type]
            image_size=config.image_size,
            max_slices_per_bag=config.max_slices_per_bag,
            batch_size=config.batch_size,
            shuffle=False,
            num_workers=config.num_workers,
        )
        prediction_frames.append(
            predict_groups(
                model=model,
                dataloader=dataloader,
                device=device,
                pooling_mode=pooling_mode,
                threshold=config.threshold,
            )
        )

    predictions_df = pd.concat(prediction_frames, ignore_index=True)

    return {
        "pooling_mode": pooling_mode,
        "best_epoch": best_epoch,
        "best_val_loss": best_val_loss,
        "history_df": pd.DataFrame(history_rows),
        "predictions_df": predictions_df,
        "checkpoint_path": checkpoint_path,
    }


def plot_confusion_matrices(
    metrics_df: pd.DataFrame,
    output_path: Path,
    split: str = "test",
) -> None:
    """Save confusion matrices for each pooling mode in one compact figure."""
    split_metrics = metrics_df[metrics_df["split"] == split].copy()
    if split_metrics.empty:
        return

    output_path.parent.mkdir(parents=True, exist_ok=True)
    n_modes = len(split_metrics)
    fig, axes = plt.subplots(1, n_modes, figsize=(4 * n_modes, 3.8), squeeze=False)

    for axis, row in zip(axes[0], split_metrics.to_dict(orient="records")):
        matrix = [[row["tn"], row["fp"]], [row["fn"], row["tp"]]]
        axis.imshow(matrix, cmap="Blues")
        axis.set_title(str(row["pooling_mode"]))
        axis.set_xticks([0, 1], labels=["Pred 0", "Pred 1"])
        axis.set_yticks([0, 1], labels=["Real 0", "Real 1"])

        for row_idx in range(2):
            for col_idx in range(2):
                axis.text(
                    col_idx,
                    row_idx,
                    str(matrix[row_idx][col_idx]),
                    ha="center",
                    va="center",
                    color="black",
                    fontsize=11,
                )

    fig.suptitle(f"Matriz de confusao MIL por grupo - split {split}")
    fig.tight_layout()
    fig.savefig(output_path, dpi=160, bbox_inches="tight")
    plt.close(fig)


def run_mil_experiment(config: MILExperimentConfig) -> dict[str, Any]:
    """
    Run group-level MIL experiments with the existing group-safe split.
    """
    set_global_seed(config.seed)
    if config.save_outputs:
        config.reports_dir.mkdir(parents=True, exist_ok=True)
        config.figures_dir.mkdir(parents=True, exist_ok=True)
    config.checkpoint_dir.mkdir(parents=True, exist_ok=True)

    all_df = load_group_safe_split(config.split_csv_path)
    all_df = filter_groups_for_smoke_test(
        all_df,
        max_groups_per_split=config.max_groups_per_split,
        seed=config.seed,
    )

    bag_summary_df = summarize_bags(all_df)
    device = get_device()

    print(f"Device: {device}")
    print(f"Split file: {config.split_csv_path}")
    print(f"Image size: {config.image_size}")
    print(f"Max slices per bag: {config.max_slices_per_bag or 'all'}")
    print("\nBag summary:")
    print(bag_summary_df.to_string(index=False))

    results = [
        train_one_pooling_mode(
            all_df=all_df,
            pooling_mode=pooling_mode,
            config=config,
            device=device,
        )
        for pooling_mode in config.pooling_modes
    ]

    predictions_df = pd.concat(
        [result["predictions_df"] for result in results],
        ignore_index=True,
    )
    metrics_df = evaluate_group_predictions(
        predictions_df=predictions_df,
        threshold=config.threshold,
    )
    history_df = pd.concat(
        [result["history_df"] for result in results],
        ignore_index=True,
    )

    output_paths: list[Path] = [result["checkpoint_path"] for result in results]
    metrics_path = config.reports_dir / "mil_experiment_metrics.csv"
    predictions_path = config.reports_dir / "mil_group_predictions.csv"
    history_path = config.reports_dir / "mil_training_history.csv"
    summary_path = config.reports_dir / "mil_experiment_summary.json"
    confusion_path = config.figures_dir / "mil_confusion_matrix.png"

    if config.save_outputs:
        metrics_df.to_csv(metrics_path, index=False, encoding="utf-8")
        predictions_df.to_csv(predictions_path, index=False, encoding="utf-8")
        history_df.to_csv(history_path, index=False, encoding="utf-8")
        plot_confusion_matrices(metrics_df, output_path=confusion_path, split="test")

        summary = {
            "experiment": "mil_por_grupo",
            "config": {key: str(value) for key, value in asdict(config).items()},
            "test_used_during_training": False,
            "best_epochs": {
                result["pooling_mode"]: int(result["best_epoch"]) for result in results
            },
            "best_val_losses": {
                result["pooling_mode"]: float(result["best_val_loss"]) for result in results
            },
        }
        with summary_path.open("w", encoding="utf-8") as file:
            json.dump(summary, file, ensure_ascii=False, indent=2)

        output_paths.extend([metrics_path, predictions_path, history_path, summary_path])
        if confusion_path.exists():
            output_paths.append(confusion_path)

    return {
        "bag_summary_df": bag_summary_df,
        "metrics_df": metrics_df,
        "predictions_df": predictions_df,
        "history_df": history_df,
        "output_paths": output_paths,
    }
