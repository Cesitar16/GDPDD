"""Genera y valida la matriz ética a partir de los datasets ya derivados.

No modifica el archivo fuente. Las cifras de evidencia se calculan desde la
versión original y la deduplicada para mantener trazabilidad reproducible.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "heart.csv"
UNIQUE = ROOT / "data" / "processed" / "heart_unique.csv"
CSV_OUT = ROOT / "outputs" / "tables" / "matriz_etica.csv"
TEX_OUT = ROOT / "docs" / "tables" / "matriz_etica.tex"

COLUMNS = [
    "ID", "Hallazgo/riesgo ético", "Evidencia", "Impacto técnico potencial",
    "Impacto ético potencial", "Mitigación", "Criterio aceptación",
]


def metrics() -> dict[str, int | float]:
    raw = pd.read_csv(RAW)
    unique = pd.read_csv(UNIQUE)
    if len(raw) != 1025 or len(unique) != 302:
        raise AssertionError("El tamaño de las fuentes no coincide con la línea base documentada.")
    return {
        "raw_n": len(raw), "duplicate_n": int(raw.duplicated().sum()), "unique_n": len(unique),
        "women": int((unique["sex"] == 0).sum()), "men": int((unique["sex"] == 1).sum()),
        "under40": int((unique["age"] < 40).sum()), "age50_59": int(unique["age"].between(50, 59).sum()),
        "over70": int((unique["age"] >= 70).sum()),
        "women_under40": int(((unique["sex"] == 0) & (unique["age"] < 40)).sum()),
        "women_over70": int(((unique["sex"] == 0) & (unique["age"] >= 70)).sum()),
    }


def pct(n: int, total: int) -> str:
    return f"{100 * n / total:.2f}".replace(".", ",")


def rows(m: dict[str, int | float]) -> list[dict[str, str]]:
    raw_n, duplicate_n, unique_n = int(m["raw_n"]), int(m["duplicate_n"]), int(m["unique_n"])
    women, men = int(m["women"]), int(m["men"])
    under40, age50_59, over70 = int(m["under40"]), int(m["age50_59"]), int(m["over70"])
    return [
        {"ID": "E01", "Hallazgo/riesgo ético": "Duplicación masiva y trazabilidad del tratamiento de datos.",
         "Evidencia": f"{raw_n} filas originales; {duplicate_n} duplicadas exactas ({pct(duplicate_n, raw_n)} %); {unique_n} únicas.",
         "Impacto técnico potencial": "Sobreponderación de patrones y posible contaminación entre particiones si se modela sin control.",
         "Impacto ético potencial": "Decisiones basadas en evidencia de calidad incierta.",
         "Mitigación": "Conservar el original, documentar deduplicación y verificar separación por registro único antes de modelar.",
         "Criterio aceptación": "CA-E01: tratamiento de duplicados documentado y verificable."},
        {"ID": "E02", "Hallazgo/riesgo ético": "Cobertura desigual por sexo.",
         "Evidencia": f"Únicos: mujeres (sex=0) {women} ({pct(women, unique_n)} %); hombres (sex=1) {men} ({pct(men, unique_n)} %).",
         "Impacto técnico potencial": "Menor evidencia para estimar desempeño futuro en el grupo menos representado.",
         "Impacto ético potencial": "Riesgo de uso inequitativo si no se evalúa la cobertura y el desempeño posterior.",
         "Mitigación": "Reportar métricas por sexo sólo al existir modelo y tamaño suficiente; no extrapolar cobertura a población.",
         "Criterio aceptación": "CA-E02 y CA-E04."},
        {"ID": "E03", "Hallazgo/riesgo ético": "Cobertura limitada en extremos etarios.",
         "Evidencia": f"Únicos: <40={under40} ({pct(under40, unique_n)} %); 50--59={age50_59} ({pct(age50_59, unique_n)} %); 70+={over70} ({pct(over70, unique_n)} %).",
         "Impacto técnico potencial": "Estimaciones inestables y generalización incierta en grupos con N reducido.",
         "Impacto ético potencial": "Posible inequidad si se usa fuera de los grupos respaldados.",
         "Mitigación": "Definir mínimo N, evaluar por edad cuando corresponda y restringir uso no respaldado.",
         "Criterio aceptación": "CA-E03 y CA-E04."},
        {"ID": "E04", "Hallazgo/riesgo ético": "Evidencia interseccional insuficiente.",
         "Evidencia": f"Mujeres <40={int(m['women_under40'])}; mujeres 70+={int(m['women_over70'])} registros únicos.",
         "Impacto técnico potencial": "Porcentajes y métricas por intersección serían altamente inestables.",
         "Impacto ético potencial": "Conclusiones aparentes podrían invisibilizar incertidumbre de grupos pequeños.",
         "Mitigación": "Informar N junto con porcentajes; no aprobar uso en combinaciones sin evidencia suficiente.",
         "Criterio aceptación": "CA-E03 y CA-E04."},
        {"ID": "E05", "Hallazgo/riesgo ético": "Diferencias descriptivas de target entre subgrupos.",
         "Evidencia": "Las proporciones de target por sexo y edad están exportadas con N en representatividad_subgrupos.csv.",
         "Impacto técnico potencial": "No permiten inferir desempeño, prevalencia ni causalidad.",
         "Impacto ético potencial": "Interpretación indebida como diferencia poblacional o discriminación.",
         "Mitigación": "Tratar resultados como descriptivos; contrastar con validación clínica/local posterior.",
         "Criterio aceptación": "CA-E05: validación con datos locales antes de uso."},
        {"ID": "E06", "Hallazgo/riesgo ético": "Cambio de dominio Kaggle hacia hospital chileno.",
         "Evidencia": "Dataset académico externo; no representa por sí mismo la población ni el flujo clínico local.",
         "Impacto técnico potencial": "Deriva de población, medición o práctica clínica; desempeño no transferible.",
         "Impacto ético potencial": "Riesgo de daños o acceso inequitativo por generalización injustificada.",
         "Mitigación": "Validación local prospectiva, documentación de población objetivo y monitoreo de deriva.",
         "Criterio aceptación": "CA-E05 y CA-E09."},
        {"ID": "E07", "Hallazgo/riesgo ético": "Automatización y posibles falsos negativos o positivos.",
         "Evidencia": "El alcance define apoyo preventivo y revisión humana; no existe modelo ni métrica clínica validada.",
         "Impacto técnico potencial": "Alertas erróneas u omisiones si un resultado se interpreta como decisión clínica.",
         "Impacto ético potencial": "Daño potencial, sesgo de automatización y dilución de responsabilidad.",
         "Mitigación": "Human in the Loop, protocolo de revisión, registro de decisión y uso exclusivamente preventivo.",
         "Criterio aceptación": "CA-E06 y CA-E10."},
        {"ID": "E08", "Hallazgo/riesgo ético": "Privacidad y gobierno del dato sensible.",
         "Evidencia": "Las alternativas Cloud, Local e Híbrida procesan datos de salud con exposiciones operacionales distintas.",
         "Impacto técnico potencial": "Acceso indebido, retención excesiva o trazabilidad insuficiente.",
         "Impacto ético potencial": "Afectación de confidencialidad y autonomía de las personas.",
         "Mitigación": "Minimización, pseudonimización, mínimos privilegios, propósito definido, retención y auditoría.",
         "Criterio aceptación": "CA-E08."},
        {"ID": "E09", "Hallazgo/riesgo ético": "Transparencia y explicabilidad insuficientes.",
         "Evidencia": "SHAP está contemplado como apoyo explicativo; no hay modelo entrenado ni auditoría de desempeño.",
         "Impacto técnico potencial": "No detectar límites o errores por subgrupo mediante explicaciones aisladas.",
         "Impacto ético potencial": "Confianza injustificada y falta de rendición de cuentas.",
         "Mitigación": "Documentar datos, límites, versiones y auditorías; SHAP complementa, no sustituye, pruebas de equidad.",
         "Criterio aceptación": "CA-E07 y CA-E09."},
    ]


def esc(text: str) -> str:
    return text.replace("&", r"\&").replace("%", r"\%").replace("_", r"\_").replace("#", r"\#")


def tex(rows_: list[dict[str, str]]) -> str:
    chunks = []
    for number, group in enumerate((rows_[:5], rows_[5:]), start=1):
        label = "tab:matriz-etica" if number == 1 else "tab:matriz-etica-cont"
        suffix = "" if number == 1 else " (continuación)"
        lines = [r"\begin{table}[H]", r"  \centering", f"  \\caption{{Matriz ética consolidada{suffix}}}", f"  \\label{{{label}}}", r"  \scriptsize", r"  \resizebox{\textwidth}{!}{%", r"  \begin{tabular}{llll}", r"    \toprule", r"    ID & Hallazgo y evidencia & Impactos potenciales & Mitigación y aceptación \\", r"    \midrule"]
        for row in group:
            evidence = f"{row['Hallazgo/riesgo ético']} {row['Evidencia']}"
            impacts = f"Técnico: {row['Impacto técnico potencial']} Ético: {row['Impacto ético potencial']}"
            mitigation = f"{row['Mitigación']} {row['Criterio aceptación']}"
            lines.append("    " + " & ".join([row["ID"], rf"\parbox[t]{{0.27\textwidth}}{{{esc(evidence)}}}", rf"\parbox[t]{{0.29\textwidth}}{{{esc(impacts)}}}", rf"\parbox[t]{{0.30\textwidth}}{{{esc(mitigation)}}}"]) + r" \\")
        lines += [r"    \bottomrule", r"  \end{tabular}%", r"  }", r"\end{table}", ""]
        chunks.extend(lines)
    return "\n".join(chunks)


def generate() -> None:
    built_rows = rows(metrics())
    CSV_OUT.parent.mkdir(parents=True, exist_ok=True)
    with CSV_OUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(built_rows)
    TEX_OUT.write_text(tex(built_rows), encoding="utf-8")


def validate() -> None:
    m = metrics()
    matrix = pd.read_csv(CSV_OUT, dtype=str, keep_default_na=False)
    if list(matrix.columns) != COLUMNS or len(matrix) != 9 or matrix["ID"].tolist() != [f"E{i:02d}" for i in range(1, 10)]:
        raise AssertionError("La matriz ética debe contener E01--E09 y las columnas requeridas.")
    required = [f"{m['duplicate_n']} duplicadas", f"mujeres (sex=0) {m['women']}", f"<40={m['under40']}", f"Mujeres <40={m['women_under40']}"]
    evidence = " ".join(matrix["Evidencia"])
    if not all(item in evidence for item in required):
        raise AssertionError("La matriz no refleja las cifras observadas requeridas.")
    if not TEX_OUT.exists():
        raise AssertionError("Falta la versión LaTeX de la matriz ética.")
    print("Validación correcta: matriz ética E01--E09 y evidencia trazable al dataset.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--validate", action="store_true")
    args = parser.parse_args()
    if not args.validate:
        generate()
    validate()
