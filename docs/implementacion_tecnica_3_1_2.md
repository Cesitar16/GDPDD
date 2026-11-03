# Actividad 3.1.2 Implementación técnica

## Alcance

El cuaderno `notebooks/04_implementacion_tecnica_3_1_2.ipynb` carga y explora `heart.csv`, audita duplicados, valores ausentes, dominios y extremos, visualiza asociaciones, compara pipelines con idéntica partición, evalúa en prueba retenida, genera cinco predicciones sintéticas y ejecuta una automatización batch. La fuente original permanece sin modificar.

## Investigación y decisiones de preparación

- **Duplicados:** el dataset tiene 1.025 filas, 723 duplicados exactos y 302 observaciones únicas. Se deduplica antes de dividir para que copias exactas no terminen a ambos lados. También se verifican combinaciones repetidas de predictores con etiquetas contradictorias: no se encontraron casos. No se conoce un identificador de paciente, así que no se puede inferir si las repeticiones originales son duplicación de publicación o múltiples observaciones de una persona.
- **Valores ausentes:** no hay nulos; no se imputa.
- **Dominios:** el diccionario del repo registra discrepancias entre esta copia y UCI para `cp`, `slope`, `ca` y `thal` (incluido `ca=4`). Se preservan y no se inventa una recodificación. Como los códigos de dolor torácico, ECG, pendiente y talio identifican categorías sin distancias cuantitativas justificadas en esta versión, los pipelines nuevos usan one-hot.
- **Valores extremos:** la regla exploratoria de 1,5×IQR marca 9 valores de `trestbps`, 5 de `chol`, 1 de `thalach` y 5 de `oldpeak`; no marca edades. Son candidatos a revisión, no errores confirmados. Se preservan, sin winsorización ni eliminación arbitraria.
- **Escalado:** la regresión logística aplica `RobustScaler` sólo a variables cuantitativas, porque puede ser sensible a escalas y valores extremos. XGBoost, basado en árboles, mantiene las cuantitativas en su escala y codifica categóricas con one-hot. Los transformadores se ajustan dentro del pipeline y de cada fold para evitar fuga.
- **Correlación:** la matriz Pearson se calcula sobre predictores cuantitativos y `target`; niveles categóricos se visualizan aparte mediante la correlación de cada indicadora de nivel con `target`. Son descripciones, no causalidad ni criterio automático para excluir variables. No se detectó una asociación cuantitativa entre predictores lo bastante alta para justificar poda por correlación.

Las decisiones siguen la recomendación de ajustar el preprocesamiento sólo sobre entrenamiento y usar pipelines durante validación cruzada; `OneHotEncoder` representa niveles categóricos como indicadores y `RobustScaler` reduce la influencia del centro y rango afectados por outliers. No se escalan las variables de XGBoost porque los modelos basados en árboles son prácticamente invariantes al escalado. Las discrepancias de dominio se contrastan con la ficha oficial UCI, que documenta la procedencia y codificaciones de la versión original: [UCI Heart Disease](https://archive.ics.uci.edu/dataset/45/heart+disease). Referencias técnicas: [prevención de fuga de datos](https://scikit-learn.org/stable/common_pitfalls.html), [codificación one-hot](https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.OneHotEncoder.html), [escalado robusto](https://scikit-learn.org/stable/modules/preprocessing.html#scaling-with-outliers) y [efecto del escalado en modelos de árboles](https://scikit-learn.org/stable/auto_examples/preprocessing/plot_scaling_importance.html).

## Gráficos y tablas generados

- `outputs/figures/matriz_correlacion_continuas_target.png`: correlación Pearson de numéricas y target.
- `outputs/figures/asociacion_niveles_categoricos_target.png`: asociación descriptiva por nivel categórico, con N en cada etiqueta.
- `outputs/figures/diagramas_caja_variables_cuantitativas.png`: revisión visual de extremos.
- `outputs/figures/distribucion_clases_antes_despues_deduplicar.png`: conteos antes y después de quitar duplicados.
- `outputs/figures/comparacion_roc_auc_validacion_cruzada.png`: media de ROC-AUC y dispersión entre folds por pipeline.
- `outputs/figures/comparacion_metricas_test_antes_despues.png`: métricas de ambos pipelines en la misma prueba retenida.
- `outputs/tables/correlacion_pearson_continuas_target.csv`, `asociacion_niveles_categoricos_target.csv` y `auditoria_extremos_iqr.csv`: cifras que respaldan los gráficos.

En la matriz Pearson sobre los 302 registros únicos, `thalach` tiene r=0,420 con target y `oldpeak` r=−0,429; la mayor correlación absoluta entre dos predictores cuantitativos es |r|=0,395 (`age` con `thalach`). Estos valores no prueban efecto causal.

## Comparación antes y después

Todos los candidatos usan la misma partición estratificada (226 train / 76 test; semilla 42). La selección se basa en ROC-AUC promedio de validación cruzada de cinco folds dentro de train. El baseline ordinal reproduce el pipeline previo; el artefacto final se selecciona entre XGBoost CUDA con codificación categórica one-hot, por la interpretación correcta de códigos categóricos y el requisito previo de usar GPU.

ROC-AUC CV: baseline XGBoost ordinal 0,917 ± 0,062; XGBoost one-hot somero 0,914 ± 0,055; XGBoost one-hot regularizado 0,913 ± 0,061. La referencia logística con RobustScaler y one-hot obtuvo 0,919 ± 0,052 en CPU. El XGBoost one-hot somero fue seleccionado para el artefacto GPU.

En el conjunto test, baseline ordinal versus XGBoost one-hot seleccionado: accuracy 0,789 vs 0,776; precision clase 1 0,791 vs 0,786; recall clase 1 0,829 vs 0,805; F1 0,810 vs 0,795; ROC-AUC 0,875 vs 0,875. Por tanto, la codificación categórica mejoró el tratamiento metodológico de los datos, pero **no mejoró las métricas predictivas en esta partición**. Las diferencias son pequeñas e inestables en 76 casos; no se deben presentar como una mejora estadísticamente demostrada. La logística CPU tuvo el mayor ROC-AUC CV, pero el modelo entregado se mantiene en GPU conforme al requisito de ejecución acordado.

## Ejecución GPU y artefactos

Entrenado localmente en NVIDIA GeForce RTX 4060 Laptop GPU, controlador 592.82, XGBoost 3.2.0 compilado con CUDA 12.9. El archivo `outputs/models/heart_disease_pipeline.joblib` registra el dispositivo `cuda:0` y las categorías admitidas por el encoder. Los cinco ejemplos de `data/samples/predicciones_ejemplo.csv` son sintéticos, no registros de pacientes; sus scores no están calibrados ni son riesgos clínicos.

El conjunto es pequeño, la versión del dataset tiene discrepancias de dominio y la semántica exacta de su etiqueta binaria no queda verificada en el archivo. Las métricas describen sólo este ejercicio académico; no acreditan diagnóstico, validez clínica ni generalización a población chilena.

## Ejecución local

```powershell
uv sync
uv run jupyter notebook notebooks/04_implementacion_tecnica_3_1_2.ipynb
```

La instalación fijada está en `pyproject.toml` y `uv.lock`. El cuaderno produce tablas y gráficos bajo `outputs/` y guarda el pipeline final en `outputs/models/heart_disease_pipeline.joblib`.

## Automatización de predicciones

```powershell
uv run python src/automatizacion_predicciones.py data/samples/predicciones_ejemplo.csv outputs/models/heart_disease_pipeline.joblib outputs/predicciones_ejemplo.csv
```

El comando valida las 13 columnas, nulos y dominios categóricos, aplica el artefacto fijado y escribe clase y score no calibrado. No reentrena ni publica modelos automáticamente.
