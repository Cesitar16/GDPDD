"""API HTTP para predicción individual y explicación SHAP."""

from pathlib import Path

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from src.explainability import explain_xgboost_pipeline
from src.modeling import CATEGORICAL_FEATURES, FEATURES, NUMERIC_FEATURES


ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT / "outputs" / "models" / "heart_disease_pipeline.joblib"
REFERENCE_PATH = ROOT / "data" / "processed" / "heart_unique.csv"
IMPORTANCE_PATH = ROOT / "outputs" / "tables" / "shap_importancia_global.csv"

app = FastAPI(title="Heart Disease Inference API", version="1.0.0")
_artifact = None
_reference = None
_importance = None


def get_artifact():
    global _artifact
    if _artifact is None:
        if not MODEL_PATH.exists():
            raise RuntimeError(f"No existe el artefacto del modelo: {MODEL_PATH}")
        _artifact = joblib.load(MODEL_PATH)
        if _artifact.get("features") != FEATURES:
            raise RuntimeError("El esquema del modelo no coincide con las variables de la API.")
        # Los contenedores usan CPU por defecto; el artefacto fue entrenado con CUDA.
        estimator = _artifact["model"].named_steps["model"]
        estimator.set_params(device="cpu")
        estimator.get_booster().set_param({"device": "cpu"})
    return _artifact


def get_reference():
    global _reference
    if _reference is None:
        _reference = pd.read_csv(REFERENCE_PATH)
    return _reference


def primitive(value):
    return value.item() if hasattr(value, "item") else value


class PredictionRequest(BaseModel):
    values: dict[str, float]


@app.get("/health")
def health():
    try:
        get_artifact()
    except Exception as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    return {"status": "ok"}


@app.get("/schema")
def schema():
    try:
        artifact = get_artifact()
        reference = get_reference()
    except Exception as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    category_domains = {
        feature: [primitive(value) for value in artifact["category_domains"][feature]]
        for feature in CATEGORICAL_FEATURES
    }
    numeric_bounds = {
        feature: [float(reference[feature].min()), float(reference[feature].max())]
        for feature in NUMERIC_FEATURES
    }
    defaults = {
        feature: primitive(reference[feature].mode().iloc[0])
        for feature in CATEGORICAL_FEATURES
    }
    defaults.update({feature: float(reference[feature].median()) for feature in NUMERIC_FEATURES})
    return {
        "features": FEATURES,
        "category_domains": category_domains,
        "numeric_bounds": numeric_bounds,
        "defaults": defaults,
    }


@app.post("/predict")
def predict(request: PredictionRequest):
    artifact = get_artifact()
    values = request.values
    missing = sorted(set(FEATURES) - set(values))
    extra = sorted(set(values) - set(FEATURES))
    if missing or extra:
        raise HTTPException(status_code=422, detail=f"Faltan variables={missing}; sobran={extra}.")
    row_data = {feature: values[feature] for feature in FEATURES}
    for feature, allowed in artifact.get("category_domains", {}).items():
        value = row_data[feature]
        if int(value) != value or int(value) not in allowed:
            raise HTTPException(
                status_code=422,
                detail=f"Categoría inválida para {feature}; valores admitidos: {allowed}.",
            )
        row_data[feature] = int(value)
    row = pd.DataFrame([row_data], columns=FEATURES)
    try:
        model = artifact["model"]
        prediction = int(model.predict(row)[0])
        score = float(model.predict_proba(row)[0, 1])
        shap_values, _, _ = explain_xgboost_pipeline(model, row)
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Falló la inferencia: {error}") from error

    local = shap_values.iloc[0].sort_values(key=lambda series: series.abs(), ascending=False)
    explanation = [
        {
            "Variable": feature,
            "Valor ingresado": primitive(row.iloc[0][feature]),
            "Contribución SHAP (log-odds)": float(local[feature]),
            "Dirección del score": "Hacia clase 1" if local[feature] > 0 else "Hacia clase 0",
        }
        for feature in local.index
    ]
    try:
        global_importance = pd.read_csv(IMPORTANCE_PATH).to_dict(orient="records")
    except FileNotFoundError:
        global_importance = []
    return {
        "prediction": prediction,
        "score_class_1_uncalibrated": score,
        "local_explanation": explanation,
        "global_importance": global_importance,
    }
