from __future__ import annotations

import numpy as np
import pandas as pd

from liverct.evaluation.classification_metrics import compute_binary_classification_metrics

METRIC_NAMES = [
    "accuracy",
    "balanced_accuracy",
    "precision",
    "recall_sensitivity",
    "specificity",
    "f1",
    "roc_auc",
    "average_precision",
]


def bootstrap_group_metrics(
    df: pd.DataFrame,
    label_col: str = "label",
    prob_col: str = "prob_positive",
    threshold: float = 0.5,
    n_bootstrap: int = 2000,
    seed: int = 42,
    ci: float = 0.95,
) -> pd.DataFrame:
    """
    Compute point estimates and percentile bootstrap CIs for binary metrics.

    Resampling is done with replacement over rows of `df` (one row per group),
    never over slices, so each resample preserves the group as the unit of
    analysis. Reuses compute_binary_classification_metrics for both the point
    estimate and every resample, to avoid a second metric implementation.
    """
    required_columns = {label_col, prob_col}
    missing = required_columns - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns in df: {sorted(missing)}")

    n_groups = len(df)
    if n_groups == 0:
        raise ValueError("df must contain at least one group row.")

    y_true = df[label_col].to_numpy()
    y_prob = df[prob_col].to_numpy()

    point_metrics = compute_binary_classification_metrics(y_true, y_prob, threshold=threshold)

    rng = np.random.default_rng(seed)
    resampled_metrics: dict[str, list[float]] = {name: [] for name in METRIC_NAMES}

    for _ in range(n_bootstrap):
        indices = rng.integers(0, n_groups, size=n_groups)
        resample_y_true = y_true[indices]
        resample_y_prob = y_prob[indices]

        if len(np.unique(resample_y_true)) < 2:
            continue

        metrics = compute_binary_classification_metrics(
            resample_y_true, resample_y_prob, threshold=threshold
        )
        for name in METRIC_NAMES:
            resampled_metrics[name].append(metrics[name])

    alpha = 1.0 - ci
    lower_pct = 100 * (alpha / 2)
    upper_pct = 100 * (1 - alpha / 2)

    rows = []
    for name in METRIC_NAMES:
        values = resampled_metrics[name]
        if values:
            ci_lower = float(np.percentile(values, lower_pct))
            ci_upper = float(np.percentile(values, upper_pct))
            n_valid_resamples = len(values)
        else:
            ci_lower = float("nan")
            ci_upper = float("nan")
            n_valid_resamples = 0

        rows.append(
            {
                "metric": name,
                "point_estimate": point_metrics[name],
                "ci_lower": ci_lower,
                "ci_upper": ci_upper,
                "n_groups": n_groups,
                "n_bootstrap": n_bootstrap,
                "n_valid_resamples": n_valid_resamples,
                "ci_level": ci,
            }
        )

    return pd.DataFrame(rows)
