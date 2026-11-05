"""Nested-CV model selection, threshold tuning, and sigmoid calibration.

Scores and labels describe only the encoded Kaggle dataset. This module does
not establish clinical validity or choose a clinically acceptable threshold.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.calibration import CalibratedClassifierCV, calibration_curve
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    brier_score_loss,
    f1_score,
    log_loss,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import (
    GridSearchCV,
    RepeatedStratifiedKFold,
    StratifiedKFold,
    cross_val_predict,
)
from sklearn.pipeline import Pipeline

from src.modeling import (
    FEATURES,
    RANDOM_STATE,
    TARGET,
    _logistic_preprocessor,
    _xgb_model,
    _xgb_preprocessor,
)


def _search_estimator_and_grid() -> tuple[Pipeline, list[dict[str, Any]]]:
    estimator = Pipeline([
        ("preprocessor", "passthrough"),
        ("model", LogisticRegression(max_iter=3000, random_state=RANDOM_STATE)),
    ])
    logistic = LogisticRegression(max_iter=3000, random_state=RANDOM_STATE)
    xgb = _xgb_model(shallow=True)
    grids: list[dict[str, Any]] = [
        {
            "preprocessor": [_logistic_preprocessor()],
            "model": [logistic],
            "model__C": [0.1, 1.0, 10.0],
            "model__class_weight": [None, "balanced"],
        },
        {
            "preprocessor": [_xgb_preprocessor()],
            "model": [xgb],
            "model__max_depth": [1, 2, 3],
            "model__n_estimators": [100, 250],
        },
    ]
    return estimator, grids


def _classification_metrics(y_true: np.ndarray, scores: np.ndarray, threshold: float) -> dict[str, float]:
    predicted = (scores >= threshold).astype(int)
    return {
        "accuracy": float(accuracy_score(y_true, predicted)),
        "balanced_accuracy": float(balanced_accuracy_score(y_true, predicted)),
        "precision_class_1": float(precision_score(y_true, predicted, zero_division=0)),
        "recall_class_1": float(recall_score(y_true, predicted, zero_division=0)),
        "specificity_class_0": float(recall_score(y_true, predicted, pos_label=0, zero_division=0)),
        "f1_class_1": float(f1_score(y_true, predicted, zero_division=0)),
    }


def _choose_threshold(y_true: np.ndarray, scores: np.ndarray, objective: str) -> float:
    candidates = np.unique(np.concatenate(([0.0, 0.5, 1.000001], scores)))
    metric = balanced_accuracy_score if objective == "balanced_accuracy" else f1_score
    scored = []
    for threshold in candidates:
        predictions = (scores >= threshold).astype(int)
        value = metric(y_true, predictions, zero_division=0) if objective == "f1" else metric(y_true, predictions)
        scored.append((float(value), -abs(float(threshold) - 0.5), float(threshold)))
    return max(scored)[2]


def nested_model_assessment(
    data: pd.DataFrame,
    *,
    n_splits: int = 5,
    n_repeats: int = 3,
    inner_splits: int = 3,
    random_state: int = RANDOM_STATE,
    output_dir: str | Path | None = None,
) -> dict[str, pd.DataFrame]:
    """Evaluate the whole model-selection procedure with repeated nested CV.

    Hyperparameters and model family are selected by inner-fold ROC-AUC.
    Thresholds are chosen on calibrated inner out-of-fold scores for two
    explicit, non-clinical objectives: balanced accuracy and F1 of class 1.
    Sigmoid calibration and all preprocessing are fitted inside each outer
    training partition. The outer folds estimate this procedure; they are not
    independent external samples.
    """
    required = FEATURES + [TARGET]
    if data.columns.tolist() != required:
        raise ValueError(f"Esquema inválido: se requiere el orden {required}.")
    if data.isna().any().any() or set(data[TARGET].unique()) != {0, 1}:
        raise ValueError("Se requieren datos sin nulos y target binario codificado 0/1.")

    unique = data.drop_duplicates().reset_index(drop=True)
    X = unique[FEATURES]
    y = unique[TARGET].astype(int).to_numpy()
    outer_cv = RepeatedStratifiedKFold(
        n_splits=n_splits, n_repeats=n_repeats, random_state=random_state
    )
    base_estimator, parameter_grid = _search_estimator_and_grid()
    metric_rows: list[dict[str, Any]] = []
    prediction_rows: list[pd.DataFrame] = []

    for split_index, (train_idx, test_idx) in enumerate(outer_cv.split(X, y)):
        repeat = split_index // n_splits + 1
        outer_fold = split_index % n_splits + 1
        X_train, X_outer = X.iloc[train_idx], X.iloc[test_idx]
        y_train, y_outer = y[train_idx], y[test_idx]
        inner_cv = StratifiedKFold(
            n_splits=inner_splits, shuffle=True, random_state=random_state + split_index + 1
        )
        search = GridSearchCV(
            estimator=base_estimator,
            param_grid=parameter_grid,
            scoring="roc_auc",
            cv=inner_cv,
            n_jobs=1,
            refit=True,
            error_score="raise",
        )
        search.fit(X_train, y_train)
        selected = search.best_estimator_
        selected_name = type(selected.named_steps["model"]).__name__
        params = {
            key: value for key, value in search.best_params_.items()
            if key not in {"model", "preprocessor"}
        }

        raw_scores = selected.predict_proba(X_outer)[:, 1]
        calibration_cv = StratifiedKFold(
            n_splits=inner_splits, shuffle=True, random_state=random_state + 10_000 + split_index
        )
        calibrated = CalibratedClassifierCV(
            estimator=clone(selected),
            method="sigmoid",
            cv=calibration_cv,
            ensemble=False,
        )
        calibrated.fit(X_train, y_train)
        calibrated_scores = calibrated.predict_proba(X_outer)[:, 1]

        # Obtain calibrated out-of-fold scores inside the outer training set;
        # these alone determine decision thresholds for this outer fold.
        threshold_cv = StratifiedKFold(
            n_splits=inner_splits, shuffle=True, random_state=random_state + 20_000 + split_index
        )
        calibrated_oof_model = CalibratedClassifierCV(
            estimator=clone(selected),
            method="sigmoid",
            cv=StratifiedKFold(
                n_splits=inner_splits,
                shuffle=True,
                random_state=random_state + 30_000 + split_index,
            ),
            ensemble=False,
        )
        calibrated_oof = cross_val_predict(
            calibrated_oof_model,
            X_train,
            y_train,
            cv=threshold_cv,
            method="predict_proba",
            n_jobs=1,
        )[:, 1]
        threshold_balanced = _choose_threshold(y_train, calibrated_oof, "balanced_accuracy")
        threshold_f1 = _choose_threshold(y_train, calibrated_oof, "f1")

        metric_row: dict[str, Any] = {
            "repeat": repeat,
            "outer_fold": outer_fold,
            "selected_model": selected_name,
            "inner_best_roc_auc": float(search.best_score_),
            "selected_params": json.dumps(params, sort_keys=True, default=str),
            "threshold_balanced_accuracy": threshold_balanced,
            "threshold_f1": threshold_f1,
            "outer_roc_auc_raw": float(roc_auc_score(y_outer, raw_scores)),
            "outer_roc_auc_calibrated": float(roc_auc_score(y_outer, calibrated_scores)),
            "outer_brier_raw": float(brier_score_loss(y_outer, raw_scores)),
            "outer_brier_calibrated": float(brier_score_loss(y_outer, calibrated_scores)),
            "outer_logloss_raw": float(log_loss(y_outer, raw_scores, labels=[0, 1])),
            "outer_logloss_calibrated": float(log_loss(y_outer, calibrated_scores, labels=[0, 1])),
        }
        for label, scores, threshold in [
            ("raw_threshold_0_5", raw_scores, 0.5),
            ("calibrated_threshold_0_5", calibrated_scores, 0.5),
            ("calibrated_threshold_balanced", calibrated_scores, threshold_balanced),
            ("calibrated_threshold_f1", calibrated_scores, threshold_f1),
        ]:
            metric_row.update({
                f"{label}_{name}": value
                for name, value in _classification_metrics(y_outer, scores, threshold).items()
            })
        metric_rows.append(metric_row)

        prediction_rows.append(pd.DataFrame({
            "unique_row_index": test_idx,
            "repeat": repeat,
            "outer_fold": outer_fold,
            "target_encoded": y_outer,
            "selected_model": selected_name,
            "score_class_1_raw": raw_scores,
            "score_class_1_sigmoid_calibrated": calibrated_scores,
            "threshold_balanced_accuracy": threshold_balanced,
            "threshold_f1": threshold_f1,
        }))

    folds = pd.DataFrame(metric_rows)
    predictions = pd.concat(prediction_rows, ignore_index=True)
    metric_cols = [
        column for column in folds.columns
        if (column.startswith("outer_") and column != "outer_fold")
        or column.startswith("raw_threshold_")
        or column.startswith("calibrated_threshold_")
        or column.startswith("threshold_")
    ]
    by_repeat = folds.groupby("repeat", as_index=False)[metric_cols].mean()
    by_repeat_summary = pd.DataFrame({
        "metric": metric_cols,
        "mean_of_repeat_means": [by_repeat[col].mean() for col in metric_cols],
        "sd_across_repeat_means": [by_repeat[col].std(ddof=1) for col in metric_cols],
    })
    family_counts = (
        folds["selected_model"].value_counts().rename_axis("selected_model")
        .reset_index(name="outer_folds_selected")
    )

    result = {
        "fold_metrics": folds,
        "repeat_means": by_repeat,
        "summary": by_repeat_summary,
        "predictions": predictions,
        "selected_model_counts": family_counts,
    }
    if output_dir is not None:
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)
        folds.to_csv(out / "nested_cv_metricas_por_fold.csv", index=False)
        by_repeat.to_csv(out / "nested_cv_metricas_por_repeticion.csv", index=False)
        by_repeat_summary.to_csv(out / "nested_cv_resumen.csv", index=False)
        predictions.to_csv(out / "nested_cv_predicciones_outer.csv", index=False)
        family_counts.to_csv(out / "nested_cv_familia_seleccionada.csv", index=False)
    return result


def plot_nested_assessment(results: dict[str, pd.DataFrame], figures_dir: str | Path) -> None:
    """Save compact diagnostics for nested metrics, calibration, and thresholds."""
    figures_dir = Path(figures_dir)
    figures_dir.mkdir(parents=True, exist_ok=True)
    folds = results["fold_metrics"]
    predictions = results["predictions"]

    fig, ax = plt.subplots(figsize=(8, 5))
    auc_by_repeat = results["repeat_means"]
    ax.plot(auc_by_repeat["repeat"], auc_by_repeat["outer_roc_auc_raw"], marker="o", label="ROC-AUC sin calibrar")
    ax.plot(auc_by_repeat["repeat"], auc_by_repeat["outer_roc_auc_calibrated"], marker="s", label="ROC-AUC calibrado")
    ax.set_xlabel("Repetición de validación externa")
    ax.set_ylabel("ROC-AUC medio en folds externos")
    ax.set_title("Evaluación anidada repetida: discriminación")
    ax.legend()
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(figures_dir / "nested_cv_roc_auc_repeticiones.png", dpi=180, bbox_inches="tight")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 6))
    for column, label in [
        ("score_class_1_raw", "Sin calibrar"),
        ("score_class_1_sigmoid_calibrated", "Calibración sigmoide"),
    ]:
        fraction, mean_predicted = calibration_curve(
            predictions["target_encoded"], predictions[column], n_bins=5, strategy="quantile"
        )
        ax.plot(mean_predicted, fraction, marker="o", label=label)
    ax.plot([0, 1], [0, 1], linestyle="--", color="gray", label="Calibración ideal")
    ax.set_xlabel("Score medio predicho para target=1")
    ax.set_ylabel("Fracción observada target=1")
    ax.set_title("Curva de confiabilidad en predicciones externas OOF")
    ax.legend()
    ax.grid(alpha=0.2)
    fig.tight_layout()
    fig.savefig(figures_dir / "nested_cv_calibracion.png", dpi=180, bbox_inches="tight")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.boxplot(
        [folds["threshold_balanced_accuracy"], folds["threshold_f1"]],
        tick_labels=["Máximo balanced accuracy", "Máximo F1 clase 1"],
        showfliers=True,
    )
    ax.axhline(0.5, color="gray", linestyle="--", label="Umbral por defecto")
    ax.set_ylabel("Umbral en score calibrado")
    ax.set_title("Umbrales elegidos sólo con datos internos de entrenamiento")
    ax.legend()
    ax.grid(axis="y", alpha=0.2)
    fig.tight_layout()
    fig.savefig(figures_dir / "nested_cv_umbral.png", dpi=180, bbox_inches="tight")
    plt.close(fig)
