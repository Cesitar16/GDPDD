from __future__ import annotations

import pandas as pd


def quality_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Resume tipo, completitud, cardinalidad y rango sin alterar los datos."""
    rows = []
    for column in df.columns:
        series = df[column]
        rows.append(
            {
                "variable": column,
                "tipo_dato": str(series.dtype),
                "nulos": int(series.isna().sum()),
                "porcentaje_nulos": float(series.isna().mean() * 100),
                "valores_unicos": int(series.nunique(dropna=True)),
                "minimo": series.min() if pd.api.types.is_numeric_dtype(series) else None,
                "maximo": series.max() if pd.api.types.is_numeric_dtype(series) else None,
            }
        )
    return pd.DataFrame(rows)


def frequency_table(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """Devuelve conteos y porcentajes de una variable discreta."""
    counts = df[column].value_counts(dropna=False).sort_index()
    return pd.DataFrame(
        {"valor": counts.index.astype(str), "conteo": counts.values,
         "porcentaje": (counts.values / len(df) * 100).round(2)}
    )


def suspicious_values(df: pd.DataFrame) -> pd.DataFrame:
    """Identifica valores que requieren revisión, sin corregir ni excluir filas."""
    checks = {
        "age": (0, 120), "trestbps": (0, 300), "chol": (0, 1000),
        "thalach": (0, 250), "oldpeak": (0, 20),
    }
    rows = []
    for column, (low, high) in checks.items():
        if column in df:
            count = int(((df[column] < low) | (df[column] > high)).sum())
            rows.append({"variable": column, "rango_revisado": f"{low} a {high}",
                         "valores_fuera_rango": count,
                         "requiere_revision": "Sí" if count else "No"})
    return pd.DataFrame(rows)
