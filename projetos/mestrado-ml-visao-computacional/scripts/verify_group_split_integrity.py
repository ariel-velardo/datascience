"""
Verifica se o split atual (train/val/test) esta livre de vazamento por
inferred_group_id.

Este script nao cria, recalcula ou modifica nenhum split. Ele reaproveita
as mesmas funcoes de validacao ja usadas em producao:

- liverct.models.cnn_dataset.validate_group_split_integrity
  (chamada por train_cnn.py, roi_experiments.py e mil_dataset.py sempre que
  um split e carregado para treino/avaliacao)
- liverct.data.split_dataset.validate_no_split_leakage
  (chamada por scripts/build_splits.py no momento em que o split e criado)

O objetivo e ter uma evidencia reproduzivel, sob demanda, de que nenhum
inferred_group_id aparece em mais de um split — sem precisar rodar um
pipeline de treino completo so para obter essa confirmacao.

Uso
---
python scripts/verify_group_split_integrity.py

Saida: relatorio no stdout + codigo de saida 0 (PASS) ou 1 (FAIL/erro).
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from liverct.data.split_dataset import validate_no_split_leakage
from liverct.models.cnn_dataset import load_split_slices, validate_group_split_integrity

SPLIT_CSV_PATH = PROJECT_ROOT / "data" / "interim" / "split_slices.csv"


def print_group_and_slice_counts(slice_df: pd.DataFrame) -> None:
    """
    Imprime contagem de grupos e slices por split e classe.
    """
    group_view = slice_df[["inferred_group_id", "split", "class_name"]].drop_duplicates(
        subset=["inferred_group_id"]
    )

    print("\nGrupos por split e classe:")
    group_counts = (
        group_view.groupby(["split", "class_name"]).size().reset_index(name="n_groups")
    )
    for row in group_counts.itertuples(index=False):
        print(f"  - {row.split:<5} | {row.class_name:<20}: {row.n_groups} grupos")

    print("\nSlices por split e classe:")
    slice_counts = (
        slice_df.groupby(["split", "class_name"]).size().reset_index(name="n_slices")
    )
    for row in slice_counts.itertuples(index=False):
        print(f"  - {row.split:<5} | {row.class_name:<20}: {row.n_slices} slices")


def main() -> int:
    if not SPLIT_CSV_PATH.exists():
        print(f"Arquivo nao encontrado: {SPLIT_CSV_PATH}")
        print(
            "Execute antes: python scripts/build_dataset_index.py "
            "&& python scripts/build_splits.py"
        )
        return 1

    slice_df = load_split_slices(SPLIT_CSV_PATH)

    print("=== VERIFICACAO DE INTEGRIDADE DO SPLIT POR GRUPO ===")
    print(f"Arquivo: {SPLIT_CSV_PATH}")
    print(f"Total de slices: {len(slice_df)}")
    print(f"Total de grupos (inferred_group_id): {slice_df['inferred_group_id'].nunique()}")

    print_group_and_slice_counts(slice_df)

    integrity_ok = True
    try:
        validate_group_split_integrity(slice_df)
    except ValueError as error:
        integrity_ok = False
        print(f"\n[FALHA] validate_group_split_integrity: {error}")

    group_view = slice_df[["inferred_group_id", "split"]].drop_duplicates()
    leakage = validate_no_split_leakage(group_view)

    print("\nLeakage entre splits (grupos presentes em mais de um split):")
    print(f"  - train-val:  {leakage['train_val_leakage']}")
    print(f"  - train-test: {leakage['train_test_leakage']}")
    print(f"  - val-test:   {leakage['val_test_leakage']}")

    leakage_ok = all(value == 0 for value in leakage.values())

    print("\n=== VEREDITO ===")
    if integrity_ok and leakage_ok:
        print("PASS: nenhum inferred_group_id aparece em mais de um split.")
        return 0

    print("FAIL: vazamento de grupo detectado. Investigue antes de treinar qualquer modelo.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
