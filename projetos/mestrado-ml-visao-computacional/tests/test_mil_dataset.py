"""
Testes de regressao para as invariantes de bag do MIL por grupo:

- uma bag deve conter exatamente um inferred_group_id;
- uma bag nao pode misturar labels;
- uma bag nao pode misturar splits.

Usa apenas dataframes sinteticos pequenos. Nao abre nenhuma imagem real:
LiverCTBagDataset so le arquivos em __getitem__, que nao e chamado aqui -
a construcao das bags (o que estamos testando) acontece em __init__.
"""

from __future__ import annotations

import unittest

import pandas as pd

from liverct.models.mil_dataset import LiverCTBagDataset


def make_clean_bags_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "file_path": ["g1_a.jpg", "g1_b.jpg", "g1_c.jpg", "g2_a.jpg", "g2_b.jpg"],
            "inferred_group_id": ["g1", "g1", "g1", "g2", "g2"],
            "label": [0, 0, 0, 1, 1],
            "split": ["train", "train", "train", "val", "val"],
        }
    )


def make_mixed_label_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "file_path": ["g3_a.jpg", "g3_b.jpg"],
            "inferred_group_id": ["g3", "g3"],
            "label": [0, 1],
            "split": ["train", "train"],
        }
    )


def make_mixed_split_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "file_path": ["g4_a.jpg", "g4_b.jpg"],
            "inferred_group_id": ["g4", "g4"],
            "label": [1, 1],
            "split": ["train", "val"],
        }
    )


class TestLiverCTBagDatasetConstruction(unittest.TestCase):
    def test_bag_contains_single_group_and_no_cross_contamination(self) -> None:
        dataset = LiverCTBagDataset(make_clean_bags_df(), image_size=32)

        self.assertEqual(len(dataset), 2)

        bags_by_group = {bag["inferred_group_id"]: bag for bag in dataset.bags}
        self.assertEqual(set(bags_by_group.keys()), {"g1", "g2"})

        g1_paths = {row["file_path"] for row in bags_by_group["g1"]["rows"]}
        g2_paths = {row["file_path"] for row in bags_by_group["g2"]["rows"]}
        self.assertEqual(g1_paths, {"g1_a.jpg", "g1_b.jpg", "g1_c.jpg"})
        self.assertEqual(g2_paths, {"g2_a.jpg", "g2_b.jpg"})

    def test_split_filter_selects_only_matching_group(self) -> None:
        dataset = LiverCTBagDataset(make_clean_bags_df(), split="train", image_size=32)

        self.assertEqual(len(dataset), 1)
        self.assertEqual(dataset.bags[0]["inferred_group_id"], "g1")

    def test_bag_raises_on_mixed_label(self) -> None:
        with self.assertRaises(ValueError):
            LiverCTBagDataset(make_mixed_label_df(), image_size=32)

    def test_bag_raises_on_mixed_split(self) -> None:
        with self.assertRaises(ValueError):
            LiverCTBagDataset(make_mixed_split_df(), image_size=32)


if __name__ == "__main__":
    unittest.main()
