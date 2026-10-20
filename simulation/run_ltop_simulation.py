"""Controlled simulation of locked-threshold operability assessment (LT-OP).

The simulation estimates a failure boundary. It does not encode an expected
direction of results and does not use real patient data.
"""

from __future__ import annotations

import argparse
import json
import platform
import sys
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sklearn
from matplotlib.lines import Line2D
from sklearn.base import clone
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier


DEVELOPMENT_N = 187
TEST_N = 61
TEST_POSITIVES = 4
RECALL_FLOOR = 0.75
THRESHOLD_SELECTION_FRACTION = 0.40
DEVELOPMENT_POSITIVES = (4, 8, 16)
SCENARIOS = ("Gaussian separated", "Gaussian high overlap", "Bernoulli weak signal")
LEARNERS = ("Logistic regression", "Decision tree")


def generate_features(rng: np.random.Generator, labels: np.ndarray, scenario: str) -> np.ndarray:
    """Generate 10 features with two weak-to-moderate signal dimensions."""
    n = len(labels)
    if scenario == "Gaussian separated":
        x = rng.normal(0.0, 1.0, size=(n, 10))
        x[:, :2] += labels[:, None] * 0.90
    elif scenario == "Gaussian high overlap":
        x = rng.normal(0.0, 1.0, size=(n, 10))
        x[:, :2] += labels[:, None] * 0.30
    elif scenario == "Bernoulli weak signal":
        probabilities = np.full((n, 10), 0.50)
        probabilities[:, :2] += labels[:, None] * 0.18
        x = rng.binomial(1, probabilities).astype(float)
    else:
        raise ValueError(f"Unknown scenario: {scenario}")
    return x


def make_dataset(rng: np.random.Generator, n: int, positives: int, scenario: str) -> tuple[np.ndarray, np.ndarray]:
    labels = np.array([1] * positives + [0] * (n - positives), dtype=int)
    rng.shuffle(labels)
    return generate_features(rng, labels, scenario), labels


def build_estimator(learner: str):
    if learner == "Logistic regression":
        return Pipeline([
            ("scale", StandardScaler()),
            ("model", LogisticRegression(C=1.0, solver="liblinear", max_iter=2000)),
        ])
    if learner == "Decision tree":
        return DecisionTreeClassifier(max_depth=2, min_samples_leaf=5, random_state=0)
    raise ValueError(f"Unknown learner: {learner}")


def choose_recall_constrained_threshold(y_true: np.ndarray, scores: np.ndarray) -> float:
    """Choose the largest score cutoff meeting the predeclared recall floor."""
    candidates = np.unique(scores)
    recalls = np.array([(scores >= threshold)[y_true == 1].mean() for threshold in candidates])
    eligible = candidates[recalls >= RECALL_FLOOR]
    if eligible.size == 0:
        raise RuntimeError("No threshold satisfies the recall floor.")
    return float(eligible.max())


def evaluate_one(
    seed: int,
    scenario: str,
    learner: str,
    development_positives: int,
) -> dict[str, float | int | str]:
    rng = np.random.default_rng(seed)
    x_dev, y_dev = make_dataset(rng, DEVELOPMENT_N, development_positives, scenario)
    x_test, y_test = make_dataset(rng, TEST_N, TEST_POSITIVES, scenario)
    # The selection scores and deployment scores must be emitted by the same
    # fitted probability function. We therefore split the development data
    # before model fitting and never refit after the threshold is chosen.
    splitter = StratifiedShuffleSplit(
        n_splits=1, test_size=THRESHOLD_SELECTION_FRACTION, random_state=seed
    )
    fit_index, threshold_index = next(splitter.split(x_dev, y_dev))
    fitted = clone(build_estimator(learner)).fit(x_dev[fit_index], y_dev[fit_index])
    threshold_scores = fitted.predict_proba(x_dev[threshold_index])[:, 1]
    threshold = choose_recall_constrained_threshold(y_dev[threshold_index], threshold_scores)
    test_scores = fitted.predict_proba(x_test)[:, 1]
    test_predicted_positive = test_scores >= threshold
    tp = int(np.sum((y_test == 1) & test_predicted_positive))
    fp = int(np.sum((y_test == 0) & test_predicted_positive))
    tn = int(np.sum((y_test == 0) & ~test_predicted_positive))
    fn = int(np.sum((y_test == 1) & ~test_predicted_positive))
    specificity = tn / (tn + fp)
    sensitivity = tp / (tp + fn)
    return {
        "seed": seed,
        "scenario": scenario,
        "learner": learner,
        "development_positives": development_positives,
        "fit_n": int(len(fit_index)),
        "fit_positives": int(y_dev[fit_index].sum()),
        "threshold_selection_n": int(len(threshold_index)),
        "threshold_selection_positives": int(y_dev[threshold_index].sum()),
        "threshold": threshold,
        "test_auc_roc": roc_auc_score(y_test, test_scores),
        "test_specificity": specificity,
        "test_sensitivity": sensitivity,
        "test_positive_fraction": float(test_predicted_positive.mean()),
        "false_positives_per_true_positive": np.nan if tp == 0 else fp / tp,
        "zero_specificity": int(specificity == 0.0),
    }


def summarize(results: pd.DataFrame) -> pd.DataFrame:
    grouped = results.groupby(["scenario", "learner", "development_positives"], observed=True)
    summary = grouped.agg(
        repetitions=("seed", "count"),
        zero_specificity_probability=("zero_specificity", "mean"),
        median_test_specificity=("test_specificity", "median"),
        q025_test_specificity=("test_specificity", lambda x: x.quantile(0.025)),
        q975_test_specificity=("test_specificity", lambda x: x.quantile(0.975)),
        median_test_auc_roc=("test_auc_roc", "median"),
        median_test_positive_fraction=("test_positive_fraction", "median"),
        median_threshold=("threshold", "median"),
    ).reset_index()
    return summary


def draw_figure(results: pd.DataFrame, output_dir: Path) -> None:
    mpl.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans", "sans-serif"],
        "font.size": 7,
        "axes.linewidth": 0.8,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "svg.fonttype": "none",
        "pdf.fonttype": 42,
    })
    scenario_order = list(SCENARIOS)
    dev_order = list(DEVELOPMENT_POSITIVES)
    fig, axes = plt.subplots(1, 3, figsize=(7.15, 2.45), constrained_layout=True)
    cmap = mpl.colormaps["YlOrRd"]
    for ax, learner, letter in zip(axes[:2], LEARNERS, ("a", "b")):
        subset = results[results["learner"] == learner]
        matrix = subset.pivot_table(
            index="scenario", columns="development_positives", values="zero_specificity", aggfunc="mean"
        ).reindex(index=scenario_order, columns=dev_order)
        im = ax.imshow(matrix.to_numpy(), vmin=0, vmax=1, cmap=cmap, aspect="auto")
        ax.set_xticks(range(len(dev_order)), dev_order)
        ax.set_yticks(range(len(scenario_order)), scenario_order if learner == LEARNERS[0] else [])
        ax.set_xlabel("Development positives")
        ax.set_title(learner, fontsize=8, fontweight="bold")
        for i in range(matrix.shape[0]):
            for j in range(matrix.shape[1]):
                value = matrix.iat[i, j]
                color = "white" if value > 0.55 else "black"
                ax.text(j, i, f"{value:.2f}", ha="center", va="center", color=color, fontsize=7)
        ax.text(-0.20, 1.05, letter, transform=ax.transAxes, fontweight="bold", fontsize=9)
    cbar = fig.colorbar(im, ax=axes[:2], shrink=0.82, pad=0.02)
    cbar.set_label("P(test specificity = 0)", fontsize=7)

    ax = axes[2]
    palette = {"Gaussian separated": "#2C7BB6", "Gaussian high overlap": "#D95F02", "Bernoulli weak signal": "#6A3D9A"}
    markers = {"Logistic regression": "o", "Decision tree": "x"}
    for scenario in scenario_order:
        for learner in LEARNERS:
            sub = results[(results["scenario"] == scenario) & (results["learner"] == learner)]
            ax.scatter(
                sub["test_auc_roc"], sub["test_specificity"], s=7, alpha=0.17,
                color=palette[scenario], marker=markers[learner], rasterized=True,
            )
    ax.axhline(0, color="#555555", lw=0.7)
    ax.set(xlabel="Independent-test AUC-ROC", ylabel="Independent-test specificity", xlim=(0, 1), ylim=(-0.03, 1.03))
    scenario_handles = [Line2D([], [], marker="o", linestyle="", color=palette[s], markersize=4, label=s) for s in scenario_order]
    learner_handles = [Line2D([], [], marker=markers[l], linestyle="", color="#333333", markersize=4, label=l) for l in LEARNERS]
    first_legend = ax.legend(handles=scenario_handles, loc="upper left", fontsize=5.6, handletextpad=0.25, labelspacing=0.3)
    ax.add_artist(first_legend)
    ax.legend(handles=learner_handles, loc="lower right", fontsize=5.6, handletextpad=0.25, labelspacing=0.3)
    ax.text(-0.20, 1.05, "c", transform=ax.transAxes, fontweight="bold", fontsize=9)
    fig.text(0.01, -0.03, "Each point is one independently generated development/test pair; panels a-b use 1,000 repetitions per cell. Thresholds were selected in an independent development subset.", fontsize=6.2)
    # Simulated-data figure; exports are generated only by the Python backend.
    fig.savefig(output_dir / "ltop_simulation.svg", bbox_inches="tight")
    fig.savefig(output_dir / "ltop_simulation.pdf", bbox_inches="tight")
    fig.savefig(output_dir / "ltop_simulation.tiff", dpi=600, bbox_inches="tight")
    fig.savefig(output_dir / "ltop_simulation_preview.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repetitions", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=20261019)
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).parent / "outputs")
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    master_rng = np.random.default_rng(args.seed)
    records = []
    for scenario in SCENARIOS:
        for learner in LEARNERS:
            for development_positives in DEVELOPMENT_POSITIVES:
                for _ in range(args.repetitions):
                    seed = int(master_rng.integers(0, np.iinfo(np.uint32).max))
                    records.append(evaluate_one(seed, scenario, learner, development_positives))
    results = pd.DataFrame(records)
    summary = summarize(results)
    results.to_csv(args.output_dir / "ltop_simulation_runs.csv", index=False)
    summary.to_csv(args.output_dir / "ltop_simulation_summary.csv", index=False)
    config = {
        "development_n": DEVELOPMENT_N,
        "test_n": TEST_N,
        "test_positives": TEST_POSITIVES,
        "development_positives": list(DEVELOPMENT_POSITIVES),
        "recall_floor": RECALL_FLOOR,
        "threshold_selection_fraction": THRESHOLD_SELECTION_FRACTION,
        "workflow": "fit model on development fitting subset; select threshold on independent development threshold-selection subset; apply same fitted model and frozen threshold to independent test set; no refit after threshold selection",
        "scenarios": list(SCENARIOS),
        "learners": list(LEARNERS),
        "repetitions": args.repetitions,
        "seed": args.seed,
        "python": sys.version,
        "platform": platform.platform(),
        "numpy": np.__version__,
        "pandas": pd.__version__,
        "scikit_learn": sklearn.__version__,
        "matplotlib": mpl.__version__,
    }
    (args.output_dir / "ltop_simulation_config.json").write_text(json.dumps(config, indent=2), encoding="utf-8")
    draw_figure(results, args.output_dir)
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
