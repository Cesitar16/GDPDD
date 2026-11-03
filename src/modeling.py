"""Reproducible baseline modeling workflow for the Heart Disease activity.

This module is educational and is not intended for clinical use.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, RobustScaler
from xgboost import XGBClassifier

TARGET = "target"
FEATURES = [
    "age", "sex", "cp", "trestbps", "chol", "fbs", "restecg",
    "thalach", "exang", "oldpeak", "slope", "ca", "thal",
]
NUMERIC_FEATURES = ["age", "trestbps", "chol", "thalach", "oldpeak"]
CATEGORICAL_FEATURES = [
    "sex", "cp", "fbs", "restecg", "exang", "slope", "ca", "thal"
]
RANDOM_STATE = 42


def _categorical_encoder() -> OneHotEncoder:
    return OneHotEncoder(handle_unknown="ignore", sparse_output=False)


def _logistic_preprocessor() -> ColumnTransformer:
    return ColumnTransformer(
        [
            ("numeric", RobustScaler(), NUMERIC_FEATURES),
            ("categorical", _categorical_encoder(), CATEGORICAL_FEATURES),
        ],
        remainder="drop",
    )


def _xgb_preprocessor() -> ColumnTransformer:
    return ColumnTransformer(
        [
            ("numeric", "passthrough", NUMERIC_FEATURES),
            ("categorical", _categorical_encoder(), CATEGORICAL_FEATURES),
        ],
        remainder="drop",
    )


def _xgb_model(*, shallow: bool = False) -> XGBClassifier:
    params = {
        "n_estimators": 250 if shallow else 200,
        "max_depth": 2 if shallow else 3,
        "learning_rate": 0.04 if shallow else 0.03,
        "min_child_weight": 3 if shallow else 5,
        "subsample": 0.9 if shallow else 0.85,
        "colsample_bytree": 0.9 if shallow else 0.85,
        "reg_lambda": 2.0 if shallow else 5.0,
        "objective": "binary:logistic",
        "eval_metric": "logloss",
        "tree_method": "hist",
        "device": "cuda",
        "random_state": RANDOM_STATE,
        "n_jobs": 4,
    }
    return XGBClassifier(**params)


def build_candidates() -> dict[str, Pipeline]:
    """Build old ordinal baseline and typed pipelines; final choice is CUDA one-hot only."""
    return {
        "Regresión logística (RobustScaler + one-hot, CPU)": Pipeline([
            ("preprocessor", _logistic_preprocessor()),
            ("model", LogisticRegression(max_iter=2000, random_state=RANDOM_STATE)),
        ]),
        "XGBoost CUDA (baseline ordinal previo)": Pipeline([
            ("model", _xgb_model(shallow=False)),
        ]),
        "XGBoost CUDA (one-hot somero)": Pipeline([
            ("preprocessor", _xgb_preprocessor()),
            ("model", _xgb_model(shallow=True)),
        ]),
        "XGBoost CUDA (one-hot regularizado)": Pipeline([
            ("preprocessor", _xgb_preprocessor()),
            ("model", _xgb_model(shallow=False)),
        ]),
    }


def train_and_evaluate(data: pd.DataFrame) -> dict[str, Any]:
    """Deduplicate exact rows, select by CV on train, and evaluate once on holdout."""
    missing = sorted(set(FEATURES + [TARGET]) - set(data.columns))
    extra = sorted(set(data.columns) - set(FEATURES + [TARGET]))
    if missing or extra:
        raise ValueError(f"Esquema inválido. Faltan={missing}; sobran={extra}.")
    if data[FEATURES + [TARGET]].isna().any().any():
        raise ValueError("El dataset contiene valores nulos; resolverlos antes de entrenar.")
    if set(data[TARGET].unique()) != {0, 1}:
        raise ValueError("La variable target debe contener las clases 0 y 1.")

    unique = data[FEATURES + [TARGET]].drop_duplicates().reset_index(drop=True)
    X, y = unique[FEATURES], unique[TARGET].astype(int)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=RANDOM_STATE, stratify=y
    )
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    candidates = build_candidates()
    rows = []
    fitted = {}
    for name, pipeline in candidates.items():
        scores = cross_val_score(
            pipeline, X_train, y_train, cv=cv, scoring="roc_auc", n_jobs=None
        )
        pipeline.fit(X_train, y_train)
        if "baseline ordinal previo" in name:
            encoding = "Códigos originales como ordinales (pipeline previo)"
        elif "logística" in name:
            encoding = "One-hot + RobustScaler numérico"
        elif "one-hot" in name:
            encoding = "Categóricas one-hot"
        else:
            encoding = "One-hot + RobustScaler numérico"
        rows.append({
            "modelo": name,
            "dispositivo": "CPU" if "logística" in name else "CUDA GPU",
            "preparación": encoding,
            "roc_auc_cv_promedio": scores.mean(),
            "roc_auc_cv_desv": scores.std(ddof=1),
        })
        fitted[name] = pipeline

    comparison = pd.DataFrame(rows).sort_values(
        "roc_auc_cv_promedio", ascending=False
    ).reset_index(drop=True)
    improved_candidates = comparison[
        comparison["modelo"].str.startswith("XGBoost CUDA (one-hot")
    ]
    if improved_candidates.empty:
        raise RuntimeError("No se entrenó ningún candidato GPU con variables categóricas one-hot.")
    selected_name = improved_candidates.iloc[0]["modelo"]
    selected = fitted[selected_name]
    predictions = selected.predict(X_test)
    probabilities = selected.predict_proba(X_test)[:, 1]
    metrics = {
        "accuracy": accuracy_score(y_test, predictions),
        "precision_clase_1": precision_score(y_test, predictions, zero_division=0),
        "recall_clase_1": recall_score(y_test, predictions, zero_division=0),
        "f1_clase_1": f1_score(y_test, predictions, zero_division=0),
        "roc_auc": roc_auc_score(y_test, probabilities),
    }
    baseline_name = "XGBoost CUDA (baseline ordinal previo)"
    baseline_model = fitted[baseline_name]
    baseline_predictions = baseline_model.predict(X_test)
    baseline_probabilities = baseline_model.predict_proba(X_test)[:, 1]
    baseline_metrics = {
        "accuracy": accuracy_score(y_test, baseline_predictions),
        "precision_clase_1": precision_score(y_test, baseline_predictions, zero_division=0),
        "recall_clase_1": recall_score(y_test, baseline_predictions, zero_division=0),
        "f1_clase_1": f1_score(y_test, baseline_predictions, zero_division=0),
        "roc_auc": roc_auc_score(y_test, baseline_probabilities),
    }
    return {
        "unique_data": unique,
        "X_train": X_train,
        "X_test": X_test,
        "y_train": y_train,
        "y_test": y_test,
        "predictions": predictions,
        "probabilities": probabilities,
        "comparison": comparison,
        "selected_name": selected_name,
        "model": selected,
        "metrics": metrics,
        "baseline_metrics": baseline_metrics,
        "baseline_name": baseline_name,
    }


def save_model(model: Pipeline, path: str | Path) -> Path:
    """Persist the fitted pipeline and its strict input contract."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    estimator = model.named_steps["model"]
    device = estimator.get_params().get("device", "cpu")
    category_domains = {}
    if "preprocessor" in model.named_steps:
        encoder = model.named_steps["preprocessor"].named_transformers_["categorical"]
        category_domains = {
            column: values.tolist()
            for column, values in zip(CATEGORICAL_FEATURES, encoder.categories_)
        }
    joblib.dump({
        "model": model,
        "features": FEATURES,
        "target": TARGET,
        "training_device": "cuda:0" if device == "cuda" else device,
        "category_domains": category_domains,
    }, path)
    return path


def predict_batch(rows: pd.DataFrame, artifact_path: str | Path) -> pd.DataFrame:
    """Validate an input batch and return class and uncalibrated class-1 score."""
    artifact = joblib.load(artifact_path)
    if rows.columns.tolist() != artifact["features"]:
        missing = sorted(set(artifact["features"]) - set(rows.columns))
        extra = sorted(set(rows.columns) - set(artifact["features"]))
        raise ValueError(
            "El CSV debe contener exactamente las 13 variables predictoras "
            f"en el orden documentado. Faltan={missing}; sobran={extra}."
        )
    if rows.empty or rows.isna().any().any():
        raise ValueError("El lote no puede estar vacío ni contener valores nulos.")
    for column, allowed in artifact.get("category_domains", {}).items():
        unknown = sorted(set(rows[column].unique()) - set(allowed))
        if unknown:
            raise ValueError(
                f"Categorías no vistas para {column}: {unknown}. "
                "Revisar el esquema y aprobar el dominio antes de inferir."
            )
    probabilities = artifact["model"].predict_proba(rows)[:, 1]
    result = rows.copy()
    result["prediction_class"] = artifact["model"].predict(rows).astype(int)
    result["score_class_1_uncalibrated"] = probabilities
    return result
