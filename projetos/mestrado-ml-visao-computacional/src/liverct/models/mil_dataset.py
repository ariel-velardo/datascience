from __future__ import annotations

from pathlib import Path
from typing import Literal

import numpy as np
import pandas as pd
import torch
from PIL import Image
from torch.utils.data import DataLoader, Dataset

from liverct.models.cnn_dataset import (
    REQUIRED_COLUMNS,
    load_split_slices,
    select_split,
    validate_group_split_integrity,
)


VALID_SPLIT = Literal["train", "val", "test"]


def load_group_safe_split(split_csv_path: str | Path) -> pd.DataFrame:
    """
    Load the existing split_slices.csv and validate group-level integrity.

    This function never creates, changes, or reassigns splits.
    """
    df = load_split_slices(split_csv_path)
    validate_group_split_integrity(df)
    return df


def filter_groups_for_smoke_test(
    df: pd.DataFrame,
    max_groups_per_split: int | None = None,
    seed: int = 42,
) -> pd.DataFrame:
    """
    Select a small balanced group subset for quick smoke tests.

    The existing split assignment is preserved. This should not be used for
    final reporting unless the reduced scope is explicitly documented.
    """
    if max_groups_per_split is None:
        return df.copy().reset_index(drop=True)

    if max_groups_per_split <= 0:
        raise ValueError("max_groups_per_split must be positive when provided.")

    selected_group_ids: list[str] = []

    group_labels = (
        df.groupby(["split", "inferred_group_id"], sort=True)
        .agg(label=("label", "first"))
        .reset_index()
    )

    for split_idx, (split_name, split_group_df) in enumerate(
        group_labels.groupby("split", sort=True)
    ):
        labels = sorted(split_group_df["label"].dropna().unique().tolist())
        per_label = max(1, max_groups_per_split // max(len(labels), 1))
        remainder = max_groups_per_split % max(len(labels), 1)

        split_selected: list[str] = []
        for label_idx, label in enumerate(labels):
            label_groups = split_group_df[split_group_df["label"] == label]
            target_n = per_label + int(label_idx < remainder)
            target_n = min(target_n, len(label_groups))
            if target_n <= 0:
                continue
            sampled = label_groups.sample(
                n=target_n,
                random_state=seed + split_idx * 101 + int(label_idx),
            )
            split_selected.extend(sampled["inferred_group_id"].astype(str).tolist())

        selected_group_ids.extend(split_selected[:max_groups_per_split])

    return (
        df[df["inferred_group_id"].astype(str).isin(selected_group_ids)]
        .copy()
        .reset_index(drop=True)
    )


def summarize_bags(df: pd.DataFrame) -> pd.DataFrame:
    """
    Summarize bag counts and slice counts by split and class.
    """
    required = {"split", "class_name", "inferred_group_id", "filename"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns in dataframe: {sorted(missing)}")

    return (
        df.groupby(["split", "class_name"], sort=True)
        .agg(
            n_bags=("inferred_group_id", "nunique"),
            n_slices=("filename", "count"),
            min_slices_per_bag=("inferred_group_id", lambda x: x.value_counts().min()),
            mean_slices_per_bag=("inferred_group_id", lambda x: x.value_counts().mean()),
            max_slices_per_bag=("inferred_group_id", lambda x: x.value_counts().max()),
        )
        .round(2)
        .reset_index()
    )


class LiverCTBagDataset(Dataset):
    """
    MIL dataset where each inferred group is one bag of CT slices.

    Each item returns all selected slices for one inferred_group_id. The group
    label is inherited from the existing split file and must be consistent
    within the bag.
    """

    def __init__(
        self,
        df: pd.DataFrame,
        split: VALID_SPLIT | None = None,
        image_size: int = 256,
        max_slices_per_bag: int | None = None,
    ) -> None:
        missing = REQUIRED_COLUMNS - set(df.columns)
        if missing:
            raise ValueError(f"Missing columns in dataframe: {sorted(missing)}")

        validate_group_split_integrity(df)

        if split is not None:
            df = select_split(df, split)
        else:
            df = df.copy()

        if max_slices_per_bag is not None and max_slices_per_bag <= 0:
            raise ValueError("max_slices_per_bag must be positive when provided.")

        self.image_size = int(image_size)
        self.max_slices_per_bag = max_slices_per_bag
        self.bags = self._build_bags(df)

    def __len__(self) -> int:
        return len(self.bags)

    def __getitem__(self, index: int) -> dict:
        bag = self.bags[index]
        rows = bag["rows"]
        images = [self._load_image(Path(row["file_path"])) for row in rows]

        return {
            "images": torch.stack(images),
            "label": torch.tensor(float(bag["label"]), dtype=torch.float32),
            "inferred_group_id": bag["inferred_group_id"],
            "split": bag["split"],
            "class_name": bag["class_name"],
            "n_slices": len(rows),
            "n_available_slices": bag["n_available_slices"],
            "file_paths": [str(row["file_path"]) for row in rows],
            "slice_ids": [row.get("slice_id") for row in rows],
            "filenames": [str(row.get("filename", "")) for row in rows],
        }

    def _build_bags(self, df: pd.DataFrame) -> list[dict]:
        sort_columns = [
            column
            for column in ["split", "class_name", "inferred_group_id", "slice_id", "filename"]
            if column in df.columns
        ]
        df = df.sort_values(sort_columns, na_position="last").reset_index(drop=True)
        bags: list[dict] = []

        for group_id, group_df in df.groupby("inferred_group_id", sort=True):
            labels = sorted(group_df["label"].dropna().unique().tolist())
            splits = sorted(group_df["split"].dropna().unique().tolist())
            if len(labels) != 1:
                raise ValueError(f"Inconsistent labels in group {group_id}: {labels}")
            if len(splits) != 1:
                raise ValueError(f"Inconsistent splits in group {group_id}: {splits}")

            selected_df = select_slices_for_bag(
                group_df,
                max_slices_per_bag=self.max_slices_per_bag,
            )

            bags.append(
                {
                    "inferred_group_id": str(group_id),
                    "split": str(splits[0]),
                    "label": int(labels[0]),
                    "class_name": str(group_df["class_name"].iloc[0])
                    if "class_name" in group_df.columns
                    else str(labels[0]),
                    "n_available_slices": int(len(group_df)),
                    "rows": selected_df.to_dict(orient="records"),
                }
            )

        if not bags:
            raise ValueError("No bags were created. Check split or input dataframe.")

        return bags

    def _load_image(self, image_path: Path) -> torch.Tensor:
        with Image.open(image_path) as image:
            image = image.convert("L")
            if image.size != (self.image_size, self.image_size):
                image = image.resize(
                    (self.image_size, self.image_size),
                    resample=Image.BILINEAR,
                )
            image_array = np.asarray(image, dtype=np.float32) / 255.0

        return torch.from_numpy(image_array).unsqueeze(0)


def select_slices_for_bag(
    group_df: pd.DataFrame,
    max_slices_per_bag: int | None,
) -> pd.DataFrame:
    """
    Select slices for one bag, preserving anatomical order when available.
    """
    sort_columns = [
        column for column in ["slice_id", "filename", "file_path"] if column in group_df.columns
    ]
    sorted_df = group_df.sort_values(sort_columns, na_position="last").reset_index(drop=True)

    if max_slices_per_bag is None or len(sorted_df) <= max_slices_per_bag:
        return sorted_df

    positions = np.linspace(0, len(sorted_df) - 1, num=max_slices_per_bag)
    selected_positions = sorted({int(round(position)) for position in positions})

    while len(selected_positions) < max_slices_per_bag:
        for position in range(len(sorted_df)):
            if position not in selected_positions:
                selected_positions.append(position)
                break

    selected_positions = sorted(selected_positions[:max_slices_per_bag])
    return sorted_df.iloc[selected_positions].reset_index(drop=True)


def collate_mil_bags(batch: list[dict]) -> dict:
    """
    Collate variable-length bags without padding.
    """
    return {
        "images": [item["images"] for item in batch],
        "label": torch.stack([item["label"] for item in batch]),
        "inferred_group_id": [item["inferred_group_id"] for item in batch],
        "split": [item["split"] for item in batch],
        "class_name": [item["class_name"] for item in batch],
        "n_slices": [item["n_slices"] for item in batch],
        "n_available_slices": [item["n_available_slices"] for item in batch],
        "file_paths": [item["file_paths"] for item in batch],
        "slice_ids": [item["slice_ids"] for item in batch],
        "filenames": [item["filenames"] for item in batch],
    }


def build_mil_dataloader(
    df: pd.DataFrame,
    split: VALID_SPLIT,
    image_size: int = 256,
    max_slices_per_bag: int | None = None,
    batch_size: int = 1,
    shuffle: bool = False,
    num_workers: int = 0,
) -> DataLoader:
    """
    Build a DataLoader for group-level MIL bags.
    """
    dataset = LiverCTBagDataset(
        df=df,
        split=split,
        image_size=image_size,
        max_slices_per_bag=max_slices_per_bag,
    )

    return DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=shuffle,
        num_workers=num_workers,
        collate_fn=collate_mil_bags,
        pin_memory=torch.cuda.is_available(),
    )
