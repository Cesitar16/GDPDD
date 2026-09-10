"""Validaciones reproducibles de calidad y representatividad de EVA1.

Este módulo sólo lee el dataset fuente y genera productos derivados para
análisis. No modifica ``data/raw/heart.csv`` ni realiza entrenamiento.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


AGE_LABELS = ["<40", "40-49", "50-59", "60-69", "70+"]


def with_age_group(df: pd.DataFrame) -> pd.DataFrame:
    """Devuelve una copia con los rangos etarios acordados."""
    result = df.copy()
    result["age_group"] = pd.cut(
        result["age"],
        bins=[0, 39, 49, 59, 69, np.inf],
        labels=AGE_LABELS,
        include_lowest=True,
    )
    return result


def duplicate_frequency(df: pd.DataFrame) -> pd.DataFrame:
    """Resume cuántas veces se repite cada observación exacta de 14 columnas."""
    repetitions = df.groupby(list(df.columns), dropna=False).size().rename("frecuencia_repeticion")
    distribution = repetitions.value_counts().sort_index()
    rows = []
    for category, frequencies in (("1", [1]), ("2", [2]), ("3", [3]), (">3", [value for value in distribution.index if value > 3])):
        distinct_count = int(sum(distribution.get(value, 0) for value in frequencies))
        associated_rows = int(sum(value * distribution.get(value, 0) for value in frequencies))
        rows.append(
            {
                "categoria_repeticion": category,
                "frecuencias_incluidas": ", ".join(str(value) for value in frequencies) if frequencies else "ninguna",
                "observaciones_distintas": distinct_count,
                "filas_originales_asociadas": associated_rows,
                "porcentaje_del_dataset_original": round(associated_rows / len(df) * 100, 2),
                "maximo_repeticiones_dataset": int(repetitions.max()),
            }
        )
    return pd.DataFrame(rows)


def category_comparison(
    original: pd.DataFrame, unique: pd.DataFrame, column: str, dimension: str | None = None
) -> pd.DataFrame:
    """Compara conteo y porcentaje de categorías entre ambas versiones."""
    categories = AGE_LABELS if column == "age_group" else sorted(set(original[column].dropna()) | set(unique[column].dropna()))
    original_counts = original[column].value_counts(dropna=False)
    unique_counts = unique[column].value_counts(dropna=False)
    rows = []
    for category in categories:
        n_original = int(original_counts.get(category, 0))
        n_unique = int(unique_counts.get(category, 0))
        pct_original = n_original / len(original) * 100
        pct_unique = n_unique / len(unique) * 100
        rows.append(
            {
                "dimension": dimension or column,
                "categoria": str(category),
                "n_original": n_original,
                "porcentaje_original": round(pct_original, 2),
                "n_unicos": n_unique,
                "porcentaje_unicos": round(pct_unique, 2),
                "diferencia_puntos_porcentuales": round(pct_unique - pct_original, 2),
            }
        )
    return pd.DataFrame(rows)


def target_by_group_comparison(original: pd.DataFrame, unique: pd.DataFrame, group: str) -> pd.DataFrame:
    """Compara target por grupo, mostrando siempre numerador y porcentaje por fila."""
    rows = []
    categories = sorted(set(original[group].dropna()) | set(unique[group].dropna()))
    for category in categories:
        row = {"grupo": group, "categoria": str(category)}
        for label, frame in (("original", original), ("unicos", unique)):
            subset = frame.loc[frame[group] == category]
            target_counts = subset["target"].value_counts()
            n = len(subset)
            row[f"n_{label}"] = n
            for target in (0, 1):
                count = int(target_counts.get(target, 0))
                row[f"target_{target}_n_{label}"] = count
                row[f"target_{target}_pct_{label}"] = round(count / n * 100, 2) if n else np.nan
        rows.append(row)
    return pd.DataFrame(rows)


def age_representation(original: pd.DataFrame, unique: pd.DataFrame) -> pd.DataFrame:
    """Estadísticos de edad, rangos y composición de target para ambas versiones."""
    rows = []
    for label, frame in (("original", original), ("unicos", unique)):
        for statistic, value in {
            "minimo": frame["age"].min(),
            "maximo": frame["age"].max(),
            "media": frame["age"].mean(),
            "mediana": frame["age"].median(),
            "desviacion_estandar": frame["age"].std(),
        }.items():
            rows.append({"dataset_evaluado": label, "tipo": "estadistico", "categoria": statistic, "valor": round(float(value), 2)})
        for group in AGE_LABELS:
            subset = frame.loc[frame["age_group"] == group]
            target_counts = subset["target"].value_counts()
            n = len(subset)
            rows.append(
                {
                    "dataset_evaluado": label,
                    "tipo": "rango_etario",
                    "categoria": group,
                    "n": n,
                    "porcentaje": round(n / len(frame) * 100, 2),
                    "target_0_n": int(target_counts.get(0, 0)),
                    "target_1_n": int(target_counts.get(1, 0)),
                    "target_0_pct_grupo": round(target_counts.get(0, 0) / n * 100, 2) if n else np.nan,
                    "target_1_pct_grupo": round(target_counts.get(1, 0) / n * 100, 2) if n else np.nan,
                }
            )
    return pd.DataFrame(rows)


def subgroup_representation(original: pd.DataFrame, unique: pd.DataFrame) -> pd.DataFrame:
    """Caracteriza la intersección sex × rango etario; no infiere sesgo demostrado."""
    rows = []
    combinations = [(sex, age_group) for sex in sorted(set(original["sex"]) | set(unique["sex"])) for age_group in AGE_LABELS]
    for sex, age_group in combinations:
        original_subset = original.loc[(original["sex"] == sex) & (original["age_group"] == age_group)]
        unique_subset = unique.loc[(unique["sex"] == sex) & (unique["age_group"] == age_group)]
        original_targets = original_subset["target"].value_counts()
        unique_targets = unique_subset["target"].value_counts()
        n_original, n_unique = len(original_subset), len(unique_subset)
        small = n_unique < 10
        rows.append(
            {
                "sex": sex,
                "age_group": age_group,
                "n_original": n_original,
                "porcentaje_original": round(n_original / len(original) * 100, 2),
                "n_unicos": n_unique,
                "porcentaje_unicos": round(n_unique / len(unique) * 100, 2),
                "target_0_n": int(unique_targets.get(0, 0)),
                "target_1_n": int(unique_targets.get(1, 0)),
                "target_0_pct": round(unique_targets.get(0, 0) / n_unique * 100, 2) if n_unique else np.nan,
                "target_1_pct": round(unique_targets.get(1, 0) / n_unique * 100, 2) if n_unique else np.nan,
                "target_0_n_original": int(original_targets.get(0, 0)),
                "target_1_n_original": int(original_targets.get(1, 0)),
                "observacion": (
                    "Subgrupo con N deduplicado reducido; los porcentajes de target son descriptivos y requieren cautela."
                    if small else "Tamaño disponible para descripción; no demuestra representatividad poblacional."
                ),
            }
        )
    return pd.DataFrame(rows)


def additional_variable_review(original: pd.DataFrame, unique: pd.DataFrame) -> pd.DataFrame:
    """Señales compactas de concentración y cambios tras deduplicación en variables discretas."""
    excluded = {"age", "trestbps", "chol", "thalach", "oldpeak", "target", "sex"}
    rows = []
    for column in original.columns:
        if column in excluded:
            continue
        original_pct = original[column].value_counts(normalize=True) * 100
        unique_pct = unique[column].value_counts(normalize=True) * 100
        categories = sorted(set(original_pct.index) | set(unique_pct.index))
        differences = [abs(unique_pct.get(value, 0) - original_pct.get(value, 0)) for value in categories]
        dominant_value = original_pct.idxmax()
        rows.append(
            {
                "variable": column,
                "categorias_observadas_original": int(original[column].nunique()),
                "categoria_mayoritaria_original": str(dominant_value),
                "porcentaje_categoria_mayoritaria_original": round(float(original_pct.loc[dominant_value]), 2),
                "maxima_diferencia_pp_original_vs_unicos": round(float(max(differences)), 2),
                "observacion": "Revisión descriptiva: requiere contraste con documentación de variables antes de cualquier interpretación clínica.",
            }
        )
    return pd.DataFrame(rows)


def findings_matrix(original: pd.DataFrame, unique: pd.DataFrame, subgroups: pd.DataFrame) -> pd.DataFrame:
    """Matriz que separa evidencia, interpretación, riesgo potencial y limitaciones."""
    sex_original = original["sex"].value_counts(normalize=True) * 100
    age_original = original["age_group"].value_counts(normalize=True) * 100
    sex_min = sex_original.idxmin()
    small_age_groups = [group for group in AGE_LABELS if age_original.get(group, 0) < 10]
    smallest = subgroups.sort_values("n_unicos").iloc[0]
    rows = [
        {
            "id": "S01", "dimension": "Calidad de datos", "dataset_evaluado": "Original",
            "evidencia": f"{int(original.duplicated().sum())} de {len(original)} filas son duplicados exactos al considerar las 14 columnas.",
            "valor_observado": f"{original.duplicated().mean() * 100:.2f}%",
            "interpretacion": "Existe una proporción alta de observaciones repetidas.",
            "posible_sesgo": "Posible problema de calidad o muestreo; no se conoce la causa de las repeticiones.",
            "impacto_tecnico_potencial": "El entrenamiento o análisis sin tratamiento podría sobreponderar observaciones repetidas.",
            "impacto_etico_potencial": "Podría afectar la confiabilidad y representatividad de resultados posteriores.",
            "limitacion_de_la_evidencia": "La coincidencia exacta no permite determinar si el origen es captura, muestreo o una característica de la fuente.",
            "mitigacion_propuesta": "Conservar el original, analizar la versión deduplicada y definir el tratamiento antes de modelar.",
            "requiere_revision": "Sí",
        },
        {
            "id": "S02", "dimension": "Representación por sex", "dataset_evaluado": "Original y deduplicado",
            "evidencia": f"sex={sex_min} representa {sex_original.loc[sex_min]:.2f}% del dataset original.",
            "valor_observado": f"sex={sex_min}: {sex_original.loc[sex_min]:.2f}%",
            "interpretacion": "La muestra presenta una distribución desigual entre los códigos de sex observados.",
            "posible_sesgo": "Posible fuente de sesgo de representación.",
            "impacto_tecnico_potencial": "Un modelo futuro podría disponer de menor evidencia para el grupo menos frecuente.",
            "impacto_etico_potencial": "Requiere evaluar resultados por subgrupo antes de cualquier uso de modelo.",
            "limitacion_de_la_evidencia": "No existe documentación local que permita asignar significado demográfico formal a sex=0 o sex=1.",
            "mitigacion_propuesta": "Mantener los códigos, verificar su definición contra la fuente oficial y evaluar métricas futuras por ambos grupos.",
            "requiere_revision": "Sí",
        },
    ]
    for group in small_age_groups:
        rows.append(
            {
                "id": f"S{len(rows)+1:02d}", "dimension": "Representación por edad", "dataset_evaluado": "Original y deduplicado",
                "evidencia": f"El rango {group} concentra {age_original.loc[group]:.2f}% del dataset original.",
                "valor_observado": f"{group}: {age_original.loc[group]:.2f}%",
                "interpretacion": "El rango etario posee pocas observaciones respecto del resto de la muestra.",
                "posible_sesgo": "Posible fuente de representación desigual; no constituye sesgo demostrado.",
                "impacto_tecnico_potencial": "Menor evidencia disponible para estimar patrones estables o desempeño futuro en este rango.",
                "impacto_etico_potencial": "Podría limitar la capacidad de generalización para ese subgrupo.",
                "limitacion_de_la_evidencia": "La distribución de la muestra no permite inferir por sí sola la distribución de la población objetivo.",
                "mitigacion_propuesta": "Documentar la limitación, contrastar con la población objetivo y evaluar subgrupos si se entrena un modelo.",
                "requiere_revision": "Sí",
            }
        )
    rows.append(
        {
            "id": f"S{len(rows)+1:02d}", "dimension": "Intersección sex × edad", "dataset_evaluado": "Deduplicado",
            "evidencia": f"La combinación sex={smallest.sex}, {smallest.age_group} posee {int(smallest.n_unicos)} observaciones deduplicadas.",
            "valor_observado": f"N único: {int(smallest.n_unicos)}",
            "interpretacion": "Es el subgrupo interseccional con menor evidencia descriptiva disponible.",
            "posible_sesgo": "Posible limitación de representatividad interseccional; no demuestra sesgo.",
            "impacto_tecnico_potencial": "Los porcentajes de target y futuras métricas en este subgrupo serían inestables.",
            "impacto_etico_potencial": "Se requiere cautela al generalizar conclusiones hacia esta combinación de grupos.",
            "limitacion_de_la_evidencia": "El análisis no establece el tamaño o composición de la población de referencia ni interpreta los códigos de sex.",
            "mitigacion_propuesta": "Reportar N junto a porcentajes y requerir validación adicional de cobertura antes de decisiones posteriores.",
            "requiere_revision": "Sí",
        }
    )
    return pd.DataFrame(rows)


def export_stage2_outputs(raw_path: Path, processed_dir: Path, tables_dir: Path) -> dict[str, pd.DataFrame]:
    """Crea la versión derivada y las tablas requeridas por la segunda etapa."""
    processed_dir.mkdir(parents=True, exist_ok=True)
    tables_dir.mkdir(parents=True, exist_ok=True)
    original_base = pd.read_csv(raw_path)
    unique_base = original_base.drop_duplicates().copy()
    unique_base.to_csv(processed_dir / "heart_unique.csv", index=False)
    original = with_age_group(original_base)
    unique = with_age_group(unique_base)

    duplicate_table = duplicate_frequency(original_base)
    comparison = pd.concat([
        category_comparison(original, unique, "target"),
        category_comparison(original, unique, "sex"),
        category_comparison(original, unique, "age_group"),
    ], ignore_index=True)
    sex_representation = pd.concat([
        target_by_group_comparison(original, unique, "sex"),
    ], ignore_index=True)
    age_table = age_representation(original, unique)
    subgroup_table = subgroup_representation(original, unique)
    target_group_table = pd.concat([
        target_by_group_comparison(original, unique, "sex"),
        target_by_group_comparison(original, unique, "age_group"),
    ], ignore_index=True)
    review = additional_variable_review(original_base, unique_base)
    findings = findings_matrix(original, unique, subgroup_table)

    outputs = {
        "analisis_duplicados": duplicate_table,
        "comparacion_original_vs_unicos": comparison,
        "representacion_sex": sex_representation,
        "representacion_edad": age_table,
        "representatividad_subgrupos": subgroup_table,
        "target_por_grupo_original_vs_unicos": target_group_table,
        "revision_variables_adicionales": review,
        "hallazgos_eda": findings,
    }
    for name, table in outputs.items():
        table.to_csv(tables_dir / f"{name}.csv", index=False, encoding="utf-8-sig")
    return outputs
