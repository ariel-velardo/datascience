"""
Testes de regressao para a selecao de checkpoint por metrica de grupo.

Cobre:
- comparacao correta entre checkpoints (val_loss vs val_group_balanced_accuracy);
- regra de desempate (F1 de grupo, depois val_loss, depois mantem o atual);
- fallback/compatibilidade com o modo val_loss legado;
- garantia de que o split de teste nunca participa da selecao de checkpoint,
  em nenhum dos dois modos.

O teste de integracao usa imagens JPEG sinteticas minusculas (16x16, ruido
aleatorio) para poder rodar liverct.models.train_cnn.run_cnn_training de
ponta a ponta em poucos segundos, sem depender do dataset real.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest import mock

import numpy as np
import pandas as pd
import torch
from PIL import Image

from liverct.models import train_cnn


class TestSelectBestCheckpointUnit(unittest.TestCase):
    def test_first_epoch_is_always_best(self) -> None:
        candidate = {
            "val_loss": 0.5,
            "val_group_balanced_accuracy": 0.6,
            "val_group_f1": 0.5,
        }
        self.assertTrue(train_cnn.select_best_checkpoint(candidate, None, "val_loss"))
        self.assertTrue(
            train_cnn.select_best_checkpoint(candidate, None, "val_group_balanced_accuracy")
        )

    def test_val_loss_mode_matches_legacy_behavior(self) -> None:
        current_best = {
            "val_loss": 0.4,
            "val_group_balanced_accuracy": 0.9,
            "val_group_f1": 0.9,
        }
        better_loss_worse_metrics = {
            "val_loss": 0.3,
            "val_group_balanced_accuracy": 0.5,
            "val_group_f1": 0.4,
        }
        worse_loss_better_metrics = {
            "val_loss": 0.5,
            "val_group_balanced_accuracy": 0.95,
            "val_group_f1": 0.95,
        }

        self.assertTrue(
            train_cnn.select_best_checkpoint(better_loss_worse_metrics, current_best, "val_loss")
        )
        self.assertFalse(
            train_cnn.select_best_checkpoint(worse_loss_better_metrics, current_best, "val_loss")
        )

    def test_group_balanced_accuracy_mode_prefers_higher_balanced_accuracy(self) -> None:
        current_best = {
            "val_loss": 0.3,
            "val_group_balanced_accuracy": 0.7,
            "val_group_f1": 0.7,
        }
        candidate = {
            "val_loss": 0.5,
            "val_group_balanced_accuracy": 0.8,
            "val_group_f1": 0.6,
        }

        self.assertTrue(
            train_cnn.select_best_checkpoint(
                candidate, current_best, "val_group_balanced_accuracy"
            )
        )

    def test_tie_break_uses_f1_then_val_loss(self) -> None:
        current_best = {
            "val_loss": 0.4,
            "val_group_balanced_accuracy": 0.8,
            "val_group_f1": 0.6,
        }

        candidate_better_f1 = {
            "val_loss": 0.5,
            "val_group_balanced_accuracy": 0.8,
            "val_group_f1": 0.7,
        }
        self.assertTrue(
            train_cnn.select_best_checkpoint(
                candidate_better_f1, current_best, "val_group_balanced_accuracy"
            )
        )

        candidate_better_val_loss = {
            "val_loss": 0.3,
            "val_group_balanced_accuracy": 0.8,
            "val_group_f1": 0.6,
        }
        self.assertTrue(
            train_cnn.select_best_checkpoint(
                candidate_better_val_loss, current_best, "val_group_balanced_accuracy"
            )
        )

        full_tie_candidate = {
            "val_loss": 0.4,
            "val_group_balanced_accuracy": 0.8,
            "val_group_f1": 0.6,
        }
        self.assertFalse(
            train_cnn.select_best_checkpoint(
                full_tie_candidate, current_best, "val_group_balanced_accuracy"
            )
        )

    def test_unknown_checkpoint_metric_raises(self) -> None:
        candidate = {
            "val_loss": 0.5,
            "val_group_balanced_accuracy": 0.6,
            "val_group_f1": 0.5,
        }
        current_best = {
            "val_loss": 0.4,
            "val_group_balanced_accuracy": 0.7,
            "val_group_f1": 0.6,
        }
        with self.assertRaises(ValueError):
            train_cnn.select_best_checkpoint(candidate, current_best, "bogus_metric")

    def test_config_default_checkpoint_metric_is_val_loss(self) -> None:
        config = train_cnn.CNNTrainingConfig(
            split_csv_path=Path("unused.csv"),
            reports_dir=Path("unused_reports"),
            checkpoint_dir=Path("unused_checkpoints"),
        )
        self.assertEqual(config.checkpoint_metric, "val_loss")
        self.assertEqual(config.artifact_prefix, "baseline_cnn")


GROUP_SPECS = [
    ("g_train_0", 0, "train"),
    ("g_train_1", 1, "train"),
    ("g_train_2", 0, "train"),
    ("g_train_3", 1, "train"),
    ("g_val_0", 0, "val"),
    ("g_val_1", 1, "val"),
    ("g_val_2", 0, "val"),
    ("g_val_3", 1, "val"),
    ("g_test_0", 0, "test"),
    ("g_test_1", 1, "test"),
]
SLICES_PER_GROUP = 3
TINY_IMAGE_SIZE = 16


def build_tiny_split_csv(root: Path, seed: int = 123) -> Path:
    """Generate tiny synthetic JPEGs + a split_slices.csv-shaped dataframe."""
    image_dir = root / "images"
    image_dir.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(seed)

    rows: list[dict[str, object]] = []
    for group_id, label, split in GROUP_SPECS:
        for slice_idx in range(SLICES_PER_GROUP):
            array = rng.integers(
                0, 256, size=(TINY_IMAGE_SIZE, TINY_IMAGE_SIZE), dtype=np.uint8
            )
            image_path = image_dir / f"{group_id}_{slice_idx}.jpg"
            Image.fromarray(array, mode="L").save(image_path, format="JPEG")
            rows.append(
                {
                    "file_path": str(image_path),
                    "label": label,
                    "split": split,
                    "inferred_group_id": group_id,
                }
            )

    split_csv_path = root / "split_slices.csv"
    pd.DataFrame(rows).to_csv(split_csv_path, index=False)
    return split_csv_path


def load_checkpoint_dict(checkpoint_path: Path) -> dict[str, object]:
    try:
        return torch.load(checkpoint_path, map_location="cpu", weights_only=False)
    except TypeError:
        return torch.load(checkpoint_path, map_location="cpu")


class TestRunCnnTrainingNeverReadsTestSplit(unittest.TestCase):
    def run_training_with_split_spy(
        self, checkpoint_metric: str
    ) -> tuple[list[str], dict[str, object]]:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            split_csv_path = build_tiny_split_csv(root)

            observed_splits: list[str] = []
            real_select_split = train_cnn.select_split

            def spy_select_split(df: pd.DataFrame, split: str) -> pd.DataFrame:
                observed_splits.append(split)
                return real_select_split(df, split)

            config = train_cnn.CNNTrainingConfig(
                split_csv_path=split_csv_path,
                reports_dir=root / "reports",
                checkpoint_dir=root / "checkpoints",
                image_size=TINY_IMAGE_SIZE,
                batch_size=4,
                epochs=3,
                patience=2,
                num_workers=0,
                checkpoint_metric=checkpoint_metric,
                artifact_prefix="tiny_group_metric",
            )

            with mock.patch.object(train_cnn, "select_split", side_effect=spy_select_split):
                result = train_cnn.run_cnn_training(config)

            result["checkpoint_dict"] = load_checkpoint_dict(result["checkpoint_path"])
            return observed_splits, result

    def test_group_balanced_accuracy_mode_never_reads_test_split(self) -> None:
        observed_splits, result = self.run_training_with_split_spy(
            "val_group_balanced_accuracy"
        )

        self.assertNotIn("test", observed_splits)
        self.assertEqual(set(observed_splits), {"train", "val"})

        history_df = result["history_df"]
        required_columns = {
            "epoch",
            "train_loss",
            "val_loss",
            "val_group_balanced_accuracy",
            "val_group_f1",
            "val_group_sensitivity",
            "val_group_specificity",
            "val_group_roc_auc",
            "val_group_average_precision",
            "is_best_checkpoint",
        }
        self.assertTrue(required_columns.issubset(set(history_df.columns)))

        checkpoint = result["checkpoint_dict"]
        required_keys = {
            "epoch",
            "selection_metric_name",
            "selection_metric_value",
            "val_loss",
            "val_group_balanced_accuracy",
            "val_group_f1",
            "val_group_sensitivity",
            "val_group_specificity",
            "val_group_roc_auc",
            "val_group_average_precision",
            "config",
            "seed",
        }
        self.assertTrue(required_keys.issubset(set(checkpoint.keys())))
        self.assertEqual(checkpoint["selection_metric_name"], "val_group_balanced_accuracy")

    def test_val_loss_mode_never_reads_test_split_either(self) -> None:
        observed_splits, result = self.run_training_with_split_spy("val_loss")

        self.assertNotIn("test", observed_splits)
        self.assertEqual(set(observed_splits), {"train", "val"})
        self.assertEqual(result["checkpoint_dict"]["selection_metric_name"], "val_loss")

    def test_val_loss_mode_selects_epoch_with_lowest_val_loss_so_far(self) -> None:
        _, result = self.run_training_with_split_spy("val_loss")
        history_df = result["history_df"]

        running_min = float("inf")
        for _, row in history_df.iterrows():
            expected_is_best = bool(row["val_loss"] < running_min)
            self.assertEqual(bool(row["is_best_checkpoint"]), expected_is_best)
            if expected_is_best:
                running_min = float(row["val_loss"])


if __name__ == "__main__":
    unittest.main()
