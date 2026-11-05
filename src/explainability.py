"""SHAP explanations for the project's one-hot XGBoost pipeline.

Attributions describe model behavior, not causal or clinical effects.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.pipeline import Pipeline

from src.modeling import CATEGORICAL_FEATURES, FEATURES, NUMERIC_FEATURES


def explain_xgboost_pipeline(
    pipeline: Pipeline, rows: pd.DataFrame
) -> tuple[pd.DataFrame, pd.Series, pd.Series]:
    """Return grouped feature SHAP values, base margins, and raw model margins.

    XGBoost's ``pred_contribs`` returns exact tree SHAP contributions on the
    raw margin (log-odds) scale. One-hot columns are summed back to their
    source categorical feature so the report has one attribution per input.
    """
    if "model" not in pipeline.named_steps:
        raise ValueError("El pipeline no contiene el estimador XGBoost.")
    if list(rows.columns) != FEATURES:
        raise ValueError("Las columnas deben coincidir con FEATURES y su orden.")

    estimator = pipeline.named_steps["model"]
    preprocessor = pipeline.named_steps.get("preprocessor")
    transformed = preprocessor.transform(rows) if preprocessor is not None else rows.to_numpy(dtype=float)
    matrix = xgb.DMatrix(
        transformed,
        feature_names=FEATURES if preprocessor is None else None,
    )
    booster = estimator.get_booster()
    raw = booster.predict(matrix, pred_contribs=True)
    margin = booster.predict(matrix, output_margin=True)

    if raw.ndim != 2 or raw.shape[1] != transformed.shape[1] + 1:
        raise RuntimeError("Forma inesperada en las contribuciones SHAP de XGBoost.")
    if not np.allclose(raw.sum(axis=1), margin, rtol=1e-5, atol=1e-5):
        raise RuntimeError("La suma de contribuciones SHAP no coincide con el margen.")

    grouped = np.zeros((len(rows), len(FEATURES)), dtype=float)
    if preprocessor is None:
        # The historical baseline passes integer category codes directly to XGBoost.
        grouped[:] = raw[:, : len(FEATURES)]
    else:
        name_to_column = {name: i for i, name in enumerate(FEATURES)}
        numeric_slice = preprocessor.output_indices_["numeric"]
        for offset, feature in enumerate(NUMERIC_FEATURES):
            grouped[:, name_to_column[feature]] = raw[:, numeric_slice.start + offset]

        categorical_slice = preprocessor.output_indices_["categorical"]
        encoder = preprocessor.named_transformers_["categorical"]
        cursor = categorical_slice.start
        for feature, categories in zip(CATEGORICAL_FEATURES, encoder.categories_):
            width = len(categories)
            grouped[:, name_to_column[feature]] = raw[:, cursor : cursor + width].sum(axis=1)
            cursor += width

    values = pd.DataFrame(grouped, index=rows.index, columns=FEATURES)
    base = pd.Series(raw[:, -1], index=rows.index, name="base_margin")
    margins = pd.Series(margin, index=rows.index, name="raw_margin")
    return values, base, margins


def summarize_shap(values: pd.DataFrame) -> pd.DataFrame:
    """Rank original input variables by mean absolute SHAP contribution."""
    return (
        pd.DataFrame(
            {
                "variable": values.columns,
                "mean_abs_shap_log_odds": values.abs().mean(axis=0).values,
                "mean_signed_shap_log_odds": values.mean(axis=0).values,
            }
        )
        .sort_values("mean_abs_shap_log_odds", ascending=False)
        .reset_index(drop=True)
    )


def plot_shap_comparison(
    onehot_summary: pd.DataFrame,
    ordinal_summary: pd.DataFrame,
    figures_dir: str | Path,
    tables_dir: str | Path,
) -> pd.DataFrame:
    """Compare global mean absolute attributions for both XGBoost pipelines."""
    import matplotlib.pyplot as plt

    figures_dir, tables_dir = Path(figures_dir), Path(tables_dir)
    comparison = onehot_summary[["variable", "mean_abs_shap_log_odds"]].merge(
        ordinal_summary[["variable", "mean_abs_shap_log_odds"]],
        on="variable", suffixes=("_onehot", "_ordinal"), validate="one_to_one",
    )
    comparison["orden_promedio"] = comparison[[
        "mean_abs_shap_log_odds_onehot", "mean_abs_shap_log_odds_ordinal"
    ]].mean(axis=1)
    comparison = comparison.sort_values("orden_promedio", ascending=False).reset_index(drop=True)
    comparison.to_csv(tables_dir / "shap_importancia_comparacion.csv", index=False)

    ordered = comparison.sort_values("orden_promedio", ascending=True)
    positions = np.arange(len(ordered))
    height = 0.38
    fig, ax = plt.subplots(figsize=(9, 7))
    ax.barh(positions - height/2, ordered["mean_abs_shap_log_odds_onehot"], height,
            label="XGBoost one-hot seleccionado", color="#4C78A8")
    ax.barh(positions + height/2, ordered["mean_abs_shap_log_odds_ordinal"], height,
            label="XGBoost ordinal (mayor accuracy test)", color="#F58518")
    ax.set_yticks(positions, ordered["variable"])
    ax.set_xlabel("Media de |SHAP| (margen log-odds)")
    ax.set_title("Contribución global por variable en ambos modelos")
    ax.legend(loc="lower right")
    fig.tight_layout()
    fig.savefig(figures_dir / "shap_importancia_comparacion.png", dpi=180, bbox_inches="tight")
    plt.close(fig)
    return comparison


def generate_explainability_artifacts(
    pipeline: Pipeline,
    unique_data: pd.DataFrame,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    y_pred: pd.Series | np.ndarray,
    class1_scores: pd.Series | np.ndarray,
    figures_dir: str | Path,
    tables_dir: str | Path,
    model_label: str = "XGBoost one-hot seleccionado",
    artifact_prefix: str = "",
) -> pd.DataFrame:
    """Build global and local SHAP summaries for the selected one-hot model."""
    import matplotlib.pyplot as plt

    figures_dir, tables_dir = Path(figures_dir), Path(tables_dir)
    figures_dir.mkdir(parents=True, exist_ok=True)
    tables_dir.mkdir(parents=True, exist_ok=True)

    suffix = f"_{artifact_prefix}" if artifact_prefix else ""
    X_all = unique_data[FEATURES]
    global_values, _, _ = explain_xgboost_pipeline(pipeline, X_all)
    summary = summarize_shap(global_values)
    summary.to_csv(tables_dir / f"shap_importancia_global{suffix}.csv", index=False)

    fig, ax = plt.subplots(figsize=(9, 6))
    ordered = summary.sort_values("mean_abs_shap_log_odds", ascending=True)
    ax.barh(ordered["variable"], ordered["mean_abs_shap_log_odds"], color="#4C78A8")
    ax.set_xlabel("Media de |SHAP| (margen log-odds)")
    ax.set_title(f"Contribuciones globales — {model_label}")
    fig.tight_layout()
    fig.savefig(figures_dir / f"shap_importancia_global{suffix}.png", dpi=180, bbox_inches="tight")
    plt.close(fig)

    # Direction plots: numerical predictors use their measured values; nominal
    # predictors use separate boxplots by category without implying category order.
    top_features = summary.head(6)["variable"].tolist()
    fig, axes = plt.subplots(2, 3, figsize=(13, 8))
    for ax, feature in zip(axes.flat, top_features):
        contributions = global_values[feature]
        if feature in NUMERIC_FEATURES:
            ax.scatter(X_all[feature], contributions, alpha=0.55, s=22, color="#4C78A8")
            ax.set_xlabel(feature)
        else:
            categories = sorted(X_all[feature].dropna().unique().tolist())
            groups = [contributions[X_all[feature].eq(category)].to_numpy() for category in categories]
            ax.boxplot(groups, tick_labels=[str(value) for value in categories], showfliers=True)
            ax.set_xlabel(f"{feature} (categorías)")
        ax.axhline(0, color="gray", linewidth=0.8, linestyle="--")
        ax.set_title(feature)
        ax.set_ylabel("Contribución SHAP a clase 1")
    for ax in axes.flat[len(top_features):]:
        ax.set_visible(False)
    fig.suptitle(f"Dirección de las contribuciones — {model_label}")
    fig.tight_layout()
    fig.savefig(figures_dir / f"shap_relacion_valor_atribucion{suffix}.png", dpi=180, bbox_inches="tight")
    plt.close(fig)

    test_values, test_base, test_margin = explain_xgboost_pipeline(pipeline, X_test)
    explanation_table = X_test.copy()
    explanation_table.insert(0, "fila_conjunto_unico", X_test.index)
    explanation_table["target_real"] = np.asarray(y_test)
    explanation_table["target_predicho"] = np.asarray(y_pred)
    explanation_table["score_clase_1_no_calibrado"] = np.asarray(class1_scores)
    explanation_table["base_margin"] = test_base.to_numpy()
    explanation_table["margen_modelo"] = test_margin.to_numpy()
    for feature in FEATURES:
        explanation_table[f"shap_{feature}"] = test_values[feature].to_numpy()
    explanation_table.to_csv(tables_dir / f"shap_contribuciones_test{suffix}.csv", index=False)

    actual = pd.Series(np.asarray(y_test), index=X_test.index)
    predicted = pd.Series(np.asarray(y_pred), index=X_test.index)
    false_negative = sorted(X_test.index[(actual == 1) & (predicted == 0)].tolist())
    false_positive = sorted(X_test.index[(actual == 0) & (predicted == 1)].tolist())
    chosen = []
    if false_negative:
        chosen.append((false_negative[0], "Falso negativo"))
    if false_positive:
        chosen.append((false_positive[0], "Falso positivo"))
    if not chosen:
        chosen.append((int(X_test.index[0]), "Caso de prueba"))

    local_rows = []
    for row_id, error_type in chosen:
        row = {
            "fila_conjunto_unico": row_id,
            "tipo_caso": error_type,
            "target_real": int(actual.loc[row_id]),
            "target_predicho": int(predicted.loc[row_id]),
            "score_clase_1_no_calibrado": float(np.asarray(class1_scores)[list(X_test.index).index(row_id)]),
            "base_margin": float(test_base.loc[row_id]),
            "margen_modelo": float(test_margin.loc[row_id]),
        }
        row.update({f"shap_{feature}": float(test_values.loc[row_id, feature]) for feature in FEATURES})
        local_rows.append(row)
    local_table = pd.DataFrame(local_rows)
    local_table.to_csv(tables_dir / f"shap_casos_error_test{suffix}.csv", index=False)

    fig, axes = plt.subplots(len(chosen), 1, figsize=(10, 4.2 * len(chosen)), squeeze=False)
    for ax, (row_id, error_type) in zip(axes.flat, chosen):
        contributions = test_values.loc[row_id].sort_values(key=lambda values: values.abs(), ascending=False)
        top = contributions.head(7)
        other = contributions.drop(top.index).sum()
        steps = list(top.items()) + [("Otras variables", float(other))]
        current = float(test_base.loc[row_id])
        y_positions = np.arange(len(steps) + 2)
        ax.barh(y_positions[0], current, left=0, color="#888888")
        ax.set_yticks(y_positions)
        ax.set_yticklabels(["Valor base"] + [name for name, _ in steps] + ["Margen final"])
        for i, (name, value) in enumerate(steps, start=1):
            color = "#E45756" if value > 0 else "#4C78A8"
            ax.barh(y_positions[i], value, left=current, color=color)
            current += value
        final_y = y_positions[-1]
        ax.scatter([float(test_margin.loc[row_id])], [final_y], color="black", zorder=3)
        score = float(np.asarray(class1_scores)[list(X_test.index).index(row_id)])
        ax.set_title(
            f"{error_type}: fila {row_id}; real={int(actual.loc[row_id])}, "
            f"predicho={int(predicted.loc[row_id])}, score clase 1={score:.3f} (no calibrado)"
        )
        ax.set_xlabel("Contribución acumulada al margen del modelo (log-odds)")
        ax.axvline(0, color="gray", linewidth=0.8)
        ax.invert_yaxis()
        ax.grid(axis="x", alpha=0.2)
    fig.suptitle(f"Descomposición SHAP de errores — {model_label}")
    fig.tight_layout()
    fig.savefig(figures_dir / f"shap_explicacion_casos_error{suffix}.png", dpi=180, bbox_inches="tight")
    plt.close(fig)

    return summary
