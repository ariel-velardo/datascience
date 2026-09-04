from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.metrics import brier_score_loss


def compute_brier_score(
    y_true: pd.Series | np.ndarray | list[int],
    y_prob: pd.Series | np.ndarray | list[float],
) -> float:
    """
    Compute the Brier score (mean squared error between predicted probability
    and observed outcome). Lower is better; 0 is a perfect probabilistic fit.
    """
    y_true_array = np.asarray(y_true).astype(int)
    y_prob_array = np.asarray(y_prob).astype(float)
    return float(brier_score_loss(y_true_array, y_prob_array))


def compute_reliability_table(
    y_true: pd.Series | np.ndarray | list[int],
    y_prob: pd.Series | np.ndarray | list[float],
    n_bins: int = 5,
) -> pd.DataFrame:
    """
    Bin predicted probabilities into n_bins equal-width bins and compare the
    mean predicted probability against the empirical (observed) frequency of
    the positive class in each bin.

    With few groups per split, some bins may end up empty (n=0); those bins
    are still reported, with NaN for mean_predicted/empirical_frequency, so
    the sparsity itself is visible rather than silently skipped.
    """
    y_true_array = np.asarray(y_true).astype(int)
    y_prob_array = np.asarray(y_prob).astype(float)

    bin_edges = np.linspace(0.0, 1.0, n_bins + 1)
    bin_indices = np.digitize(y_prob_array, bin_edges[1:-1], right=False)

    rows = []
    for bin_idx in range(n_bins):
        mask = bin_indices == bin_idx
        n = int(mask.sum())

        rows.append(
            {
                "bin_lower": float(bin_edges[bin_idx]),
                "bin_upper": float(bin_edges[bin_idx + 1]),
                "mean_predicted": float(y_prob_array[mask].mean()) if n > 0 else float("nan"),
                "empirical_frequency": float(y_true_array[mask].mean()) if n > 0 else float("nan"),
                "n": n,
            }
        )

    return pd.DataFrame(rows)
