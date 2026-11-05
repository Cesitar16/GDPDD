# Heart Disease — prototipo académico

Proyecto académico de Gestión de Proyectos de Datos. La línea base vigente es de diez semanas e incluye preparación y análisis del dataset Heart Disease, un modelo experimental entrenado localmente con GPU y automatización batch demostrativa. El presupuesto de referencia EP3 es CLP 10.506.069 (estimación académica; no gasto observado ni cotización).

## Dataset

El archivo original se conserva en `data/raw/heart.csv`. Es inmutable: no debe limpiarse, sobrescribirse ni usarse como destino de datos procesados.

## Estructura

- `notebooks/`: análisis secuencial de calidad, evidencia para sesgos y consolidación final.
- `src/`: funciones reutilizables para calidad, análisis por grupos y gráficos.
- `outputs/tables/` y `outputs/figures/`: artefactos utilizables posteriormente en LaTeX.
- `handoffs/`: plantillas para comunicar hallazgos a planificación y riesgos.
- `docs/`: informe maestro LaTeX alineado con los informes EP3/3.2.2 y el estado actual del prototipo.

## Uso

```powershell
uv sync
uv run jupyter notebook
```

Ejecute los notebooks en este orden:

1. `01_eda_calidad.ipynb`
2. `02_eda_sesgos.ipynb`
3. `03_resultados_finales.ipynb`
4. `04_implementacion_tecnica_3_1_2.ipynb`

La actividad 3.1.2 incluye un flujo de modelado con XGBoost CUDA y gráficos. En Windows con GPU NVIDIA, prepare el entorno con `uv sync` y abra el cuaderno con `uv run jupyter notebook notebooks/04_implementacion_tecnica_3_1_2.ipynb`. Los resultados, decisiones y límites se documentan en `docs/implementacion_tecnica_3_1_2.md` y en el informe maestro.

El modelo es experimental: no está validado clínicamente ni desplegado. Los scores no están calibrados y las cinco filas de ejemplo son sintéticas. El proyecto vigente no incluye operación posterior a diez semanas ni arquitectura productiva Cloud/Local/Híbrida.

Inicie Jupyter desde la raíz del proyecto para conservar las rutas relativas.
