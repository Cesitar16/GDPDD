"""Error and subgroup audit for the existing held-out test explanations."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

FEATURES = [
    "age", "sex", "cp", "trestbps", "chol", "fbs", "restecg",
    "thalach", "exang", "oldpeak", "slope", "ca", "thal",
]
SHAP_COLUMNS = [f"shap_{feature}" for feature in FEATURES]


def _wilson(successes: int, total: int, z: float = 1.959963984540054) -> tuple[float, float]:
    if total == 0:
        return np.nan, np.nan
    proportion = successes / total
    denominator = 1 + z**2 / total
    center = (proportion + z**2 / (2 * total)) / denominator
    half_width = z * np.sqrt(
        proportion * (1 - proportion) / total + z**2 / (4 * total**2)
    ) / denominator
    return center - half_width, center + half_width


def _age_group(age: float) -> str:
    if age < 40:
        return "<40"
    if age < 50:
        return "40–49"
    if age < 60:
        return "50–59"
    if age < 70:
        return "60–69"
    return "70+"


def _subgroup_metrics(data: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    groups: list[tuple[str, str, pd.DataFrame]] = [("overall", "Todos", data)]
    groups.extend(
        ("sex", f"sex={value}", group)
        for value, group in data.groupby("sex", sort=True, dropna=False)
    )
    groups.extend(
        ("age_group", str(value), group)
        for value, group in data.groupby("age_group", sort=False, dropna=False)
    )

    for dimension, label, group in groups:
        actual = group["target_real"].astype(int)
        predicted = group["target_predicho"].astype(int)
        tp = int(((actual == 1) & (predicted == 1)).sum())
        fn = int(((actual == 1) & (predicted == 0)).sum())
        tn = int(((actual == 0) & (predicted == 0)).sum())
        fp = int(((actual == 0) & (predicted == 1)).sum())
        positives, negatives = tp + fn, tn + fp
        recall = tp / positives if positives else np.nan
        specificity = tn / negatives if negatives else np.nan
        recall_low, recall_high = _wilson(tp, positives)
        specificity_low, specificity_high = _wilson(tn, negatives)
        n = len(group)
        rows.append({
            "dimension": dimension,
            "grupo": label,
            "n": n,
            "target_0_n": negatives,
            "target_1_n": positives,
            "tn": tn,
            "fp": fp,
            "fn": fn,
            "tp": tp,
            "accuracy": (tp + tn) / n if n else np.nan,
            "recall_target_1": recall,
            "recall_ci95_low": recall_low,
            "recall_ci95_high": recall_high,
            "specificity_target_0": specificity,
            "specificity_ci95_low": specificity_low,
            "specificity_ci95_high": specificity_high,
            "small_support_flag": bool(n < 10 or positives < 5 or negatives < 5),
        })
    return pd.DataFrame(rows)


def _plot_error_shap(errors: pd.DataFrame, figures_dir: Path) -> None:
    ordered = errors.sort_values(
        ["error_type", "fila_conjunto_unico"],
        ascending=[True, True],
        key=lambda values: values.map({"Falso negativo": 0, "Falso positivo": 1})
        if values.name == "error_type" else values,
    )
    values = ordered[SHAP_COLUMNS].to_numpy(dtype=float)
    labels = [
        f"{row.error_type} · fila {row.fila_conjunto_unico}"
        for row in ordered.itertuples()
    ]
    height = max(6, 0.42 * len(ordered))
    fig, ax = plt.subplots(figsize=(12, height))
    limit = max(float(np.nanmax(np.abs(values))), 0.1)
    mesh = ax.imshow(values, aspect="auto", cmap="RdBu_r", vmin=-limit, vmax=limit)
    ax.set_yticks(np.arange(len(labels)), labels=labels, fontsize=8)
    ax.set_xticks(np.arange(len(FEATURES)), labels=FEATURES, rotation=45, ha="right")
    ax.set_title("Contribuciones SHAP en todos los errores del test")
    ax.set_xlabel("Variable; rojo empuja el score hacia target=1 y azul hacia target=0")
    ax.set_ylabel("Caso de prueba (ID técnico del conjunto deduplicado)")
    fig.colorbar(mesh, ax=ax, label="Contribución al margen (log-odds)")
    fig.tight_layout()
    fig.savefig(figures_dir / "shap_mapa_errores_test.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def _plot_error_summary(summary: pd.DataFrame, figures_dir: Path) -> None:
    top_features = (
        summary.groupby("variable")["mean_abs_shap_log_odds"]
        .mean().nlargest(10).index.tolist()
    )
    plot_data = summary[summary["variable"].isin(top_features)].copy()
    pivot = plot_data.pivot(
        index="variable", columns="error_type", values="mean_abs_shap_log_odds"
    ).reindex(top_features)
    fig, ax = plt.subplots(figsize=(10, 6))
    pivot.plot(kind="barh", ax=ax, color={"Falso negativo": "#4C78A8", "Falso positivo": "#F58518"})
    ax.set_xlabel("Media de |SHAP| entre errores (log-odds)")
    ax.set_ylabel("Variable")
    ax.set_title("Variables con mayor contribución absoluta entre errores")
    ax.legend(title="Tipo de error")
    ax.invert_yaxis()
    fig.tight_layout()
    fig.savefig(figures_dir / "shap_resumen_errores_test.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def _plot_subgroup_metrics(metrics: pd.DataFrame, figures_dir: Path) -> None:
    subset = metrics[metrics["dimension"].isin(["overall", "sex", "age_group"])].copy()
    subset["label"] = subset.apply(
        lambda row: f"{row.dimension}: {row.grupo} (n={row.n}; +{row.target_1_n}/−{row.target_0_n})",
        axis=1,
    )
    y = np.arange(len(subset))
    fig, ax = plt.subplots(figsize=(12, max(6, 0.48 * len(subset))))
    for metric, low, high, offset, color, label in [
        ("recall_target_1", "recall_ci95_low", "recall_ci95_high", -0.11, "#4C78A8", "Recall target=1"),
        ("specificity_target_0", "specificity_ci95_low", "specificity_ci95_high", 0.11, "#F58518", "Especificidad target=0"),
    ]:
        center = subset[metric].to_numpy(dtype=float)
        low_err = center - subset[low].to_numpy(dtype=float)
        high_err = subset[high].to_numpy(dtype=float) - center
        ax.errorbar(
            center, y + offset, xerr=np.vstack([low_err, high_err]),
            fmt="o", capsize=3, color=color, label=label,
        )
    ax.set_yticks(y, labels=subset["label"])
    ax.set_xlim(-0.03, 1.03)
    ax.set_xlabel("Proporción en test; barras = intervalos Wilson 95 %")
    ax.set_title("Rendimiento descriptivo por subgrupo (test retenido)")
    ax.grid(axis="x", alpha=0.25)
    ax.legend(loc="lower right")
    fig.tight_layout()
    fig.savefig(figures_dir / "metricas_test_por_subgrupo.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def generate_error_bias_audit(
    explanations_csv: str | Path,
    tables_dir: str | Path = "outputs/tables",
    figures_dir: str | Path = "outputs/figures",
) -> dict[str, pd.DataFrame]:
    """Create per-error SHAP and descriptive subgroup metrics from held-out rows."""
    explanations_csv = Path(explanations_csv)
    tables_dir, figures_dir = Path(tables_dir), Path(figures_dir)
    tables_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)
    data = pd.read_csv(explanations_csv)
    required = {
        "fila_conjunto_unico", "age", "sex", "target_real", "target_predicho",
        "score_clase_1_no_calibrado", *SHAP_COLUMNS,
    }
    missing = sorted(required - set(data.columns))
    if missing:
        raise ValueError(f"Faltan columnas requeridas en las explicaciones: {missing}")
    if data.empty:
        raise ValueError("El CSV de explicaciones no contiene observaciones.")

    data["age_group"] = data["age"].map(_age_group)
    data["error_type"] = np.select(
        [
            (data["target_real"] == 1) & (data["target_predicho"] == 0),
            (data["target_real"] == 0) & (data["target_predicho"] == 1),
        ],
        ["Falso negativo", "Falso positivo"],
        default="Correcto",
    )
    errors = data[data["error_type"] != "Correcto"].copy()
    errors.to_csv(tables_dir / "errores_test_por_caso.csv", index=False)

    summary_rows = []
    for error_type, group in errors.groupby("error_type", sort=True):
        for feature in FEATURES:
            values = group[f"shap_{feature}"]
            summary_rows.append({
                "error_type": error_type,
                "n_errores": len(group),
                "variable": feature,
                "mean_abs_shap_log_odds": values.abs().mean(),
                "mean_signed_shap_log_odds": values.mean(),
                "proporcion_empuja_target_1": (values > 0).mean(),
                "proporcion_empuja_target_0": (values < 0).mean(),
            })
    error_summary = pd.DataFrame(summary_rows).sort_values(
        ["error_type", "mean_abs_shap_log_odds"], ascending=[True, False]
    )
    error_summary.to_csv(tables_dir / "shap_resumen_errores_test.csv", index=False)

    subgroup_metrics = _subgroup_metrics(data)
    subgroup_metrics.to_csv(tables_dir / "metricas_test_por_subgrupo.csv", index=False)

    _plot_error_shap(errors, figures_dir)
    _plot_error_summary(error_summary, figures_dir)
    _plot_subgroup_metrics(subgroup_metrics, figures_dir)
    return {
        "errores": errors,
        "resumen_shap_errores": error_summary,
        "metricas_subgrupos": subgroup_metrics,
    }


if __name__ == "__main__":
    result = generate_error_bias_audit("outputs/tables/shap_contribuciones_test.csv")
    counts = result["errores"]["error_type"].value_counts().to_dict()
    print(f"Errores analizados: {counts}")
    print(f"Tablas: outputs/tables; figuras: outputs/figures")
