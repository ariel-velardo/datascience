"""
Testes de regressao para a invariante central do projeto: nenhum
inferred_group_id pode aparecer em mais de um split (train/val/test).

Usa apenas dataframes sinteticos pequenos, sem dataset real e sem GPU.
"""

from __future__ import annotations

import unittest

import pandas as pd

from liverct.data.split_dataset import validate_no_split_leakage
from liverct.models.cnn_dataset import validate_group_split_integrity


def make_clean_split_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "inferred_group_id": ["g1", "g1", "g2", "g2", "g3"],
            "split": ["train", "train", "val", "val", "test"],
        }
    )


def make_leaking_split_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "inferred_group_id": ["g1", "g1", "g2", "g2", "g3"],
            "split": ["train", "val", "val", "val", "test"],
        }
    )


class TestValidateNoSplitLeakage(unittest.TestCase):
    def test_clean_split_has_zero_leakage(self) -> None:
        leakage = validate_no_split_leakage(make_clean_split_df())
        self.assertEqual(
            leakage,
            {"train_val_leakage": 0, "train_test_leakage": 0, "val_test_leakage": 0},
        )

    def test_group_in_two_splits_is_detected(self) -> None:
        leakage = validate_no_split_leakage(make_leaking_split_df())
        self.assertEqual(leakage["train_val_leakage"], 1)
        self.assertEqual(leakage["train_test_leakage"], 0)
        self.assertEqual(leakage["val_test_leakage"], 0)


class TestValidateGroupSplitIntegrity(unittest.TestCase):
    def test_clean_split_does_not_raise(self) -> None:
        validate_group_split_integrity(make_clean_split_df())

    def test_leaking_split_raises_value_error(self) -> None:
        with self.assertRaises(ValueError):
            validate_group_split_integrity(make_leaking_split_df())


if __name__ == "__main__":
    unittest.main()
