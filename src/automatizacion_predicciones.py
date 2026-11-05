"""CLI for repeatable batch inference with a previously validated artifact."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

try:
    from .modeling import predict_batch
except ImportError:  # direct execution: python src/automatizacion_predicciones.py
    from modeling import predict_batch


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Valida un CSV y genera predicciones educativas Heart Disease."
    )
    parser.add_argument("input_csv", type=Path, help="CSV con las 13 variables predictoras")
    parser.add_argument("model", type=Path, help="Pipeline .joblib previamente validado")
    parser.add_argument("output_csv", type=Path, help="Ruta del CSV de salida")
    args = parser.parse_args()

    batch = pd.read_csv(args.input_csv)
    predictions = predict_batch(batch, args.model)
    predictions.insert(
        0, "generated_at_utc", datetime.now(timezone.utc).isoformat(timespec="seconds")
    )
    args.output_csv.parent.mkdir(parents=True, exist_ok=True)
    predictions.to_csv(args.output_csv, index=False)
    print(f"Predicciones generadas: {len(predictions)}")
    print(f"Salida: {args.output_csv.resolve()}")
    print("El score de clase 1 no está calibrado ni representa riesgo clínico.")


if __name__ == "__main__":
    main()
