"""Audit the local heart.csv against the public Kaggle source and its metadata."""

from __future__ import annotations

import hashlib
import io
import json
from pathlib import Path
from urllib.request import Request, urlopen

import pandas as pd

from src.modeling import FEATURES, TARGET

KAGGLE_REF = "johnsmith88/heart-disease-dataset"
KAGGLE_METADATA_URL = f"https://www.kaggle.com/api/v1/datasets/view/{KAGGLE_REF}"
KAGGLE_CSV_URL = (
    f"https://www.kaggle.com/api/v1/datasets/download/{KAGGLE_REF}?fileName=heart.csv"
)


def _download(url: str) -> bytes:
    request = Request(url, headers={"User-Agent": "heart-disease-model-audit/1.0"})
    with urlopen(request, timeout=45) as response:
        return response.read()


def audit_local_source(path: str | Path, *, verify_online: bool = True) -> pd.DataFrame:
    """Return auditable provenance facts; online verification is optional.

    The source author's metadata is recorded as a provider claim. Exact file
    matching verifies provenance to that Kaggle artifact, not clinical labels.
    """
    path = Path(path)
    local_bytes = path.read_bytes()
    local = pd.read_csv(io.BytesIO(local_bytes))
    required = FEATURES + [TARGET]
    if local.columns.tolist() != required:
        raise ValueError("heart.csv no coincide con el esquema documentado.")

    rows: list[dict[str, str | int | bool]] = []

    def add(item: str, value: object, interpretation: str) -> None:
        rows.append({"elemento": item, "valor": str(value), "interpretacion": interpretation})

    add("archivo_local", str(path), "Fuente utilizada por el proyecto.")
    add("sha256_local", hashlib.sha256(local_bytes).hexdigest(), "Huella del archivo auditado.")
    add("filas_locales", len(local), "Número de filas antes de deduplicar.")
    add("duplicados_exactos", int(local.duplicated().sum()), "Copias exactas sobre las 14 columnas.")
    unique = local.drop_duplicates().reset_index(drop=True)
    add("filas_unicas", len(unique), "Observaciones distintas tras deduplicación exacta.")
    add("target_conteos_original", json.dumps(local[TARGET].value_counts().sort_index().to_dict()), "Conteos por código de etiqueta.")
    add("target_conteos_unicos", json.dumps(unique[TARGET].value_counts().sort_index().to_dict()), "Conteos tras deduplicación exacta.")
    conflicts = int((local.groupby(FEATURES, dropna=False)[TARGET].nunique() > 1).sum())
    add("combinaciones_predictoras_con_etiquetas_conflictivas", conflicts, "Grupos de predictores idénticos con target distinto.")

    if verify_online:
        metadata = json.loads(_download(KAGGLE_METADATA_URL))
        source_bytes = _download(KAGGLE_CSV_URL)
        source = pd.read_csv(io.BytesIO(source_bytes))
        exact_table_match = local.equals(source)
        description = metadata.get("descriptionNullable") or metadata.get("description") or ""
        normalized = " ".join(str(description).lower().split())
        if "0 = no disease" in normalized and "1 = disease" in normalized:
            target_claim = "Kaggle declara target=0 sin enfermedad y target=1 con enfermedad."
        else:
            target_claim = "La ficha consultada no contiene una declaración binaria inequívoca de target."
        add("fuente_publicada", KAGGLE_REF, "Dataset de Kaggle declarado por el proyecto.")
        add("version_kaggle_consultada", metadata.get("currentVersionNumberNullable", "desconocida"), "Versión devuelta por la API de Kaggle al ejecutar esta auditoría.")
        add("coincidencia_tabular_exacta_con_kaggle", exact_table_match, "Comparación de valores, columnas y orden tras leer ambos CSV.")
        add("definicion_target_del_proveedor", target_claim, "Declaración del proveedor; no es validación clínica independiente.")
        add("huella_csv_fuente", hashlib.sha256(source_bytes).hexdigest(), "Huella del archivo descargado de Kaggle durante la auditoría.")
    else:
        add("verificacion_online", False, "No se consultó la fuente remota en esta ejecución.")

    for column, expected in {
        "cp": "la ficha UCI describe cuatro categorías, pero no se trazó la recodificación de esta copia",
        "slope": "los códigos observados no se reconciliaron registro a registro con UCI",
        "ca": "heart.csv observa 0--4 frente al dominio UCI descrito 0--3",
        "thal": "heart.csv observa 0--3 y la ficha Kaggle describe 0--2",
    }.items():
        add(f"dominio_{column}", "|".join(map(str, sorted(unique[column].dropna().unique()))), expected)

    add("validacion_externa", "no disponible", "El repositorio no contiene una cohorte independiente, autorizada y compatible.")
    add("alcance_etiqueta", "positivo=target 1 codificado", "Se sigue la ficha del proveedor; equivalencia clínica y población de origen no verificadas independientemente.")
    return pd.DataFrame(rows)
