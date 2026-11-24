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
5. `05_evaluacion_robusta_modelo.ipynb` (validación anidada; complementaria)
6. `06_auditoria_errores_y_subgrupos.ipynb` (requiere salidas del notebook 04)

La actividad 3.1.2 incluye un flujo de modelado con XGBoost CUDA y gráficos. En Windows con GPU NVIDIA, prepare el entorno con `uv sync` y abra el cuaderno con `uv run jupyter notebook notebooks/04_implementacion_tecnica_3_1_2.ipynb`. La evaluación robusta complementaria está en el notebook 05; las explicaciones de todos los errores y las métricas por subgrupo, en el notebook 06. La síntesis para revisión del proceso del modelo está en `docs/explicabilidad_y_auditoria_modelo.md`; el detalle técnico en `docs/implementacion_tecnica_3_1_2.md` y la memoria LaTeX específica en `docs/modelo.tex`.

El modelo es experimental: no está validado clínicamente ni desplegado. Los scores no están calibrados y las cinco filas de ejemplo son sintéticas. El proyecto vigente no incluye operación posterior a diez semanas ni arquitectura productiva Cloud/Local/Híbrida.

## Interfaz interactiva (prototipo)

La interfaz Streamlit permite ingresar los 13 predictores, obtener una predicción del pipeline guardado y revisar las contribuciones SHAP por caso. La API de inferencia se ejecuta en un servicio separado. Con Docker Desktop y Compose activos, inicia ambos servicios desde la raíz del proyecto:

```powershell
docker compose up --build -d
```

Abre [http://localhost:8501](http://localhost:8501). La API queda disponible solo dentro de la red de Compose; la interfaz es el único puerto publicado. Para revisar el estado y los logs:

```powershell
docker compose ps
docker compose logs -f model-api interface
```

Para detener los contenedores:

```powershell
docker compose down
```

La interfaz ofrece dos botones de perfiles ficticios para ejecutar una demostración sin llenar el formulario. También ofrece una vista profesional de lectura simple y una vista técnica. La primera presenta el reparto relativo de las contribuciones SHAP por perfil y una conclusión en lenguaje directo; la segunda muestra los valores SHAP en log-odds. El score del modelo y el porcentaje de contribución no son probabilidades clínicas. El modelo acertó 59 de 76 casos (77,6 %) en una prueba interna: esa cifra describe el conjunto de prueba y no estima la probabilidad de acierto de un perfil individual.

`model-api` carga `outputs/models/heart_disease_pipeline.joblib`, sirve predicciones y explicaciones SHAP, y cambia el dispositivo de inferencia a CPU para funcionar en Docker sin GPU. Es un prototipo educativo, no una herramienta clínica.

Inicie Jupyter desde la raíz del proyecto para conservar las rutas relativas.
