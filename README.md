# EVA1 Heart Disease EDA

Proyecto académico de Gestión de Proyectos de Datos para evaluar la calidad y explorar el dataset Heart Disease antes de cualquier análisis posterior de posibles sesgos.

## Dataset

El archivo original se conserva en `data/raw/heart.csv`. Es inmutable: no debe limpiarse, sobrescribirse ni usarse como destino de datos procesados.

## Estructura

- `notebooks/`: análisis secuencial de calidad, evidencia para sesgos y consolidación final.
- `src/`: funciones reutilizables para calidad, análisis por grupos y gráficos.
- `outputs/tables/` y `outputs/figures/`: artefactos utilizables posteriormente en LaTeX.
- `handoffs/`: plantillas para comunicar hallazgos a planificación y riesgos.
- `docs/`: documentación LaTeX existente, mantenida sin modificaciones por este flujo EDA.

## Uso

```powershell
python -m pip install -r requirements.txt
jupyter notebook
```

Ejecute los notebooks en este orden:

1. `01_eda_calidad.ipynb`
2. `02_eda_sesgos.ipynb`
3. `03_resultados_finales.ipynb`

Inicie Jupyter desde la raíz del proyecto para conservar las rutas relativas.
