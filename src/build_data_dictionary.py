"""Genera y valida el diccionario de datos de la fuente inmutable heart.csv."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RAW_DATA = ROOT / "data" / "raw" / "heart.csv"
DICTIONARY = ROOT / "data" / "dictionary" / "diccionario_datos.csv"
LATEX_TABLE = ROOT / "docs" / "tables" / "diccionario_datos.tex"

COLUMNS = [
    "variable", "rol", "tipo_dato", "tipo_variable", "categoria",
    "descripcion", "unidad", "codificacion", "min_observado",
    "max_observado", "valores_observados", "nulos", "valores_unicos",
    "fuente_definicion", "observacion_calidad", "relevancia_etica",
]

UCI = "UCI Heart Disease Dataset y archivo heart-disease.names"
KAGGLE = "Kaggle JohnSmith88 Heart Disease Dataset"
SOURCE = f"{UCI}; {KAGGLE}; heart.csv (valores observados)"

METADATA = {
    "age": ("Predictor", "Numérica discreta", "Demográfica", "Edad del paciente.", "años", "No aplica.", "Sin discrepancia de codificación observada.", "Alta relevancia para analizar cobertura y representatividad etaria."),
    "sex": ("Predictor", "Binaria", "Demográfica", "Sexo del paciente.", "No aplica.", "UCI: 0=mujer; 1=hombre.", "Los valores observados coinciden con la codificación binaria documentada por UCI; la trazabilidad exacta de la recodificación de Kaggle no se documenta por separado.", "Alta relevancia para evaluar representación y, posteriormente, desempeño por sexo."),
    "cp": ("Predictor", "Categórica", "Clínica", "Tipo de dolor torácico.", "No aplica.", "UCI original: 1=angina típica; 2=angina atípica; 3=dolor no anginoso; 4=asintomático.", "UCI documenta 1--4, pero heart.csv observa 0--3. Codificación específica de esta versión no verificada de forma concluyente.", "Relevante para interpretar diferencias clínicas; no implica sesgo por sí sola."),
    "trestbps": ("Predictor", "Numérica discreta", "Clínica", "Presión arterial en reposo al ingreso.", "mmHg", "No aplica.", "Sin discrepancia de codificación observada.", "Relevante para interpretar el perfil clínico y su cobertura."),
    "chol": ("Predictor", "Numérica discreta", "Clínica", "Colesterol sérico.", "mg/dL", "No aplica.", "Sin discrepancia de codificación observada.", "Relevante para interpretar el perfil clínico y su cobertura."),
    "fbs": ("Predictor", "Binaria", "Clínica", "Indicador de glucosa en ayunas superior a 120 mg/dL.", "No aplica.", "UCI: 1=verdadero; 0=falso.", "Los valores observados son binarios y coinciden con el dominio documentado.", "Relevante para interpretar el perfil clínico y su cobertura."),
    "restecg": ("Predictor", "Categórica", "Clínica", "Resultado del electrocardiograma en reposo.", "No aplica.", "UCI: 0=normal; 1=anormalidad ST-T; 2=hipertrofia ventricular izquierda probable/definida.", "Los valores observados 0, 1 y 2 coinciden con el dominio UCI.", "Relevante para interpretar el perfil clínico y su cobertura."),
    "thalach": ("Predictor", "Numérica discreta", "Clínica", "Frecuencia cardíaca máxima alcanzada.", "bpm", "No aplica.", "Sin discrepancia de codificación observada.", "Relevante para interpretar el perfil clínico y su cobertura."),
    "exang": ("Predictor", "Binaria", "Clínica", "Angina inducida por ejercicio.", "No aplica.", "UCI: 1=sí; 0=no.", "Los valores observados son binarios y coinciden con el dominio documentado.", "Relevante para interpretar el perfil clínico y su cobertura."),
    "oldpeak": ("Predictor", "Numérica continua", "Clínica", "Depresión del segmento ST inducida por ejercicio respecto del reposo.", "desviación ST", "No aplica.", "Sin discrepancia de codificación observada.", "Relevante para interpretar el perfil clínico y su cobertura."),
    "slope": ("Predictor", "Categórica", "Clínica", "Pendiente del segmento ST durante ejercicio.", "No aplica.", "UCI original: 1=ascendente; 2=plana; 3=descendente.", "UCI documenta 1--3, pero heart.csv observa 0--2. Codificación específica de esta versión no verificada de forma concluyente.", "Relevante para interpretar el perfil clínico y su cobertura."),
    "ca": ("Predictor", "Numérica discreta", "Clínica", "Número de vasos principales coloreados por fluoroscopia.", "conteo", "UCI original: 0--3.", "heart.csv observa 0--4, mientras UCI documenta 0--3. Se conserva el valor 4 sin reinterpretarlo.", "Relevante para interpretar el perfil clínico y su cobertura."),
    "thal": ("Predictor", "Categórica", "Clínica", "Resultado de la prueba de talio.", "No aplica.", "UCI original: 3=normal; 6=defecto fijo; 7=defecto reversible.", "heart.csv observa 0--3, distinto de 3, 6 y 7 de UCI. Codificación específica de esta versión no verificada de forma concluyente.", "Relevante para interpretar el perfil clínico y su cobertura."),
    "target": ("Target", "Binaria", "Resultado", "Variable objetivo binaria de la versión Kaggle, asociada a la presencia de enfermedad cardíaca.", "No aplica.", "UCI original usa num=0 (ausencia) y 1--4 (presencia). heart.csv usa target binario 0/1; el mapeo exacto de la recodificación Kaggle no está documentado de forma concluyente.", "El dominio observado es binario; se mantiene sin alterar. La versión deriva conceptualmente de la variable num de UCI.", "Alta relevancia porque define el resultado para análisis posterior."),
}

TABLE_CODING = {
    "age": "años", "sex": "0=mujer; 1=hombre", "cp": "No verificada; ver CSV",
    "trestbps": "mmHg", "chol": "mg/dL", "fbs": "0=no; 1=sí (>120 mg/dL)",
    "restecg": "0=normal; 1=ST-T; 2=HVI", "thalach": "bpm", "exang": "0=no; 1=sí",
    "oldpeak": "desviación ST", "slope": "No verificada; ver CSV", "ca": "UCI: 0--3; CSV: 0--4",
    "thal": "No verificada; ver CSV", "target": "Binaria 0/1; ver CSV",
}


def scalar(value: object) -> str:
    value = float(value)
    return str(int(value)) if value.is_integer() else format(value, "g")


def observed(series: pd.Series) -> str:
    return "|".join(scalar(x) for x in sorted(series.dropna().unique()))


def build_rows(data: pd.DataFrame) -> list[dict[str, str]]:
    if list(data.columns) != list(METADATA):
        raise ValueError(f"Columnas inesperadas: {list(data.columns)}")
    rows = []
    for variable in data.columns:
        role, variable_type, category, description, unit, coding, quality, ethics = METADATA[variable]
        series = data[variable]
        rows.append({
            "variable": variable,
            "rol": role,
            "tipo_dato": str(series.dtype),
            "tipo_variable": variable_type,
            "categoria": category,
            "descripcion": description,
            "unidad": unit,
            "codificacion": coding,
            "min_observado": scalar(series.min()),
            "max_observado": scalar(series.max()),
            "valores_observados": observed(series),
            "nulos": str(int(series.isna().sum())),
            "valores_unicos": str(int(series.nunique(dropna=True))),
            "fuente_definicion": SOURCE,
            "observacion_calidad": quality,
            "relevancia_etica": ethics,
        })
    return rows


def tex_escape(text: str) -> str:
    return text.replace("&", r"\&").replace("%", r"\%").replace("_", r"\_")


def tex_row(row: dict[str, str]) -> str:
    domain = (
        row["valores_observados"]
        if row["tipo_variable"] in {"Binaria", "Categórica"}
        else f'{row["min_observado"]}--{row["max_observado"]}'
    )
    return " & ".join(map(tex_escape, [row["variable"], row["descripcion"], row["tipo_variable"], TABLE_CODING[row["variable"]], domain])) + " \\\\"


def write_latex(rows: list[dict[str, str]]) -> None:
    LATEX_TABLE.parent.mkdir(parents=True, exist_ok=True)
    groups = [rows[:7], rows[7:]]
    parts = []
    for index, group in enumerate(groups, start=1):
        suffix = "" if index == 1 else " (continuación)"
        label = "tab:diccionario-datos" if index == 1 else "tab:diccionario-datos-cont"
        parts.extend([
            r"\begin{table}[H]", r"  \centering",
            f"  \\caption{{Diccionario resumido de variables{suffix}}}", f"  \\label{{{label}}}",
            r"  \scriptsize", r"  \resizebox{\textwidth}{!}{%", r"  \begin{tabular}{lllll}",
            r"    \toprule", r"    Variable & Descripción & Tipo & Unidad / codificación & Dominio observado \\", r"    \midrule",
        ])
        parts.extend("    " + tex_row(row).rstrip("\n") for row in group)
        parts.extend([r"    \bottomrule", r"  \end{tabular}%", r"  }", r"\end{table}", ""])
    LATEX_TABLE.write_text("\n".join(parts), encoding="utf-8")


def generate() -> None:
    data = pd.read_csv(RAW_DATA)
    rows = build_rows(data)
    DICTIONARY.parent.mkdir(parents=True, exist_ok=True)
    with DICTIONARY.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    write_latex(rows)


def validate() -> None:
    data = pd.read_csv(RAW_DATA)
    dictionary = pd.read_csv(DICTIONARY, dtype=str, keep_default_na=False)
    if list(dictionary.columns) != COLUMNS or len(dictionary) != 14:
        raise AssertionError("El diccionario debe tener exactamente 14 filas y las columnas requeridas.")
    if dictionary["variable"].duplicated().any() or set(dictionary["variable"]) != set(data.columns):
        raise AssertionError("Las variables del diccionario no coinciden exactamente con heart.csv.")
    indexed = dictionary.set_index("variable")
    for variable in data.columns:
        series = data[variable]
        expected = {
            "min_observado": scalar(series.min()), "max_observado": scalar(series.max()),
            "valores_observados": observed(series), "nulos": str(int(series.isna().sum())),
            "valores_unicos": str(int(series.nunique(dropna=True))),
        }
        for field, value in expected.items():
            if indexed.at[variable, field] != value:
                raise AssertionError(f"{variable}.{field}: {indexed.at[variable, field]} != {value}")
    print("Validación correcta: 14/14 variables y todos los metadatos observados coinciden con heart.csv.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--validate", action="store_true")
    args = parser.parse_args()
    if not args.validate:
        generate()
    validate()
