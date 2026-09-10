from __future__ import annotations

import pandas as pd


def distribution(df: pd.DataFrame, column: str) -> pd.DataFrame:
    counts = df[column].value_counts(dropna=False).sort_index()
    return pd.DataFrame({column: counts.index, "conteo": counts.values,
                         "porcentaje": (counts.values / len(df) * 100).round(2)})


def target_by_group(df: pd.DataFrame, group: str, target: str = "target") -> pd.DataFrame:
    counts = pd.crosstab(df[group], df[target])
    within_group = pd.crosstab(df[group], df[target], normalize="index") * 100
    result = counts.reset_index()
    for value in counts.columns:
        result[f"target_{value}_porcentaje_grupo"] = within_group[value].round(2).values
    return result


def age_groups(df: pd.DataFrame) -> pd.Series:
    return pd.cut(df["age"], bins=[0, 39, 49, 59, 69, 200],
                  labels=["<40", "40-49", "50-59", "60-69", "70+"], include_lowest=True)


def findings_matrix(df: pd.DataFrame, age_group: pd.Series) -> pd.DataFrame:
    """Registra evidencia observada; no diagnostica discriminación."""
    rows = []
    sex_share = df["sex"].value_counts(normalize=True).sort_index() * 100
    minority = sex_share.idxmin()
    rows.append({"id": "S01", "dimension": "sex",
                 "evidencia": "El grupo menos representado por sex concentra una proporción menor de la muestra.",
                 "valor_observado": f"sex={minority}: {sex_share.loc[minority]:.2f}%",
                 "posible_problema": "Representación desigual entre grupos.",
                 "tipo_sesgo_potencial": "Posible sesgo de representación.",
                 "impacto_potencial": "Un eventual modelo podría generalizar peor para el grupo menos representado.",
                 "requiere_revision": "Sí"})
    age_share = age_group.value_counts(normalize=True, sort=False) * 100
    for group, share in age_share.items():
        if share < 10:
            rows.append({"id": f"S{len(rows)+1:02d}", "dimension": "age_group",
                         "evidencia": "El rango etario presenta una participación inferior al 10% de la muestra.",
                         "valor_observado": f"{group}: {share:.2f}%",
                         "posible_problema": "Grupo etario poco representado.",
                         "tipo_sesgo_potencial": "Posible sesgo de representación.",
                         "impacto_potencial": "Menor estabilidad descriptiva y posible menor generalización futura.",
                         "requiere_revision": "Sí"})
    duplicate_share = df.duplicated().mean() * 100
    if duplicate_share > 0:
        rows.append({"id": f"S{len(rows)+1:02d}", "dimension": "calidad_datos",
                     "evidencia": "Se observan filas duplicadas exactas en el dataset original.",
                     "valor_observado": f"{int(df.duplicated().sum())} duplicados ({duplicate_share:.2f}%)",
                     "posible_problema": "Sobre-representación de registros repetidos.",
                     "tipo_sesgo_potencial": "Posible riesgo de representatividad.",
                     "impacto_potencial": "Podría afectar análisis descriptivos y una evaluación futura de modelos.",
                     "requiere_revision": "Sí"})
    return pd.DataFrame(rows)
