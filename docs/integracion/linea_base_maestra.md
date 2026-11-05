# Línea base maestra vigente — Heart Disease

## Alcance temporal y financiero

- Referencia vigente: `Informe_EP3_Cardiaco_CORREGIDO_Desarrollador_Full_Stack (1).pdf`.
- Horizonte académico de diez semanas: 5 de octubre–13 de diciembre de 2026.
- Presupuesto estimado: CLP 10.506.069, para prototipo de investigación y demostración; no es cotización ni gasto observado.
- No se define presupuesto ni plan de operación posterior al cierre académico.
- `Informe_Actividad_3_2_2_Monitoreo_Control_Heart_Disease.pdf` se conserva como ejercicio de monitoreo y control con simulaciones. No sustituye calendario/presupuesto EP3 ni demuestra ejecución material.

## Estado actual del repositorio

- Dataset `heart.csv`: 1.025 filas, 14 variables, 723 duplicados exactos y 302 registros únicos; sin nulos detectados en la auditoría.
- Notebook `notebooks/04_implementacion_tecnica_3_1_2.ipynb`: preparación reproducible, EDA, comparación de candidatos, evaluación, cinco predicciones sintéticas y automatización batch.
- Código de apoyo: `src/modeling.py`, `src/automatizacion_predicciones.py`; entorno fijado con `uv` en `pyproject.toml` y `uv.lock`.
- Artefacto: `outputs/models/heart_disease_pipeline.joblib`, XGBoost one-hot entrenado en CUDA (`cuda:0`) en NVIDIA GeForce RTX 4060 Laptop GPU.
- Resultados y gráficos: `outputs/figures/`, `outputs/tables/`; resumen y decisiones en `docs/implementacion_tecnica_3_1_2.md` y `docs/sections/08_modelado_y_resultados.tex`.
- No hay producto clínico desplegado, conexión institucional, validación local, aprobación clínica ni operación posterior documentada.

## Evaluación del modelo

- Partición estratificada: 226 train / 76 test, semilla 42; CV de cinco folds.
- ROC-AUC CV: logística CPU 0,919 ± 0,052; XGBoost ordinal baseline 0,917 ± 0,062; XGBoost one-hot somero 0,914 ± 0,055; XGBoost one-hot regularizado 0,913 ± 0,061.
- Test baseline ordinal vs XGBoost one-hot seleccionado: accuracy 0,789 vs 0,776; precisión clase 1 0,791 vs 0,786; recall 0,829 vs 0,805; F1 0,810 vs 0,795; ROC-AUC 0,875 vs 0,875.
- La codificación categórica one-hot es metodológicamente preferible para las variables tratadas, pero no mejoró las métricas de esta partición. El candidato GPU se conserva por el requisito académico de ejecución en GPU, no por superioridad predictiva.
- El conjunto pequeño, las diferencias de dominio y la falta de validación local impiden conclusiones clínicas o de generalización. Scores de ejemplo no calibrados; filas de ejemplo sintéticas.

## Decisiones de datos

- Se deduplicó antes de particionar; no se detectaron combinaciones repetidas de predictores con etiquetas contradictorias.
- Sin nulos, no se imputó.
- Se preservaron categorías discrepantes y valores extremos no confirmados como errores.
- RobustScaler se aplica sólo a variables cuantitativas del comparador logístico; árboles no escalan cuantitativas. Transformaciones se ajustan dentro de pipeline/fold.
- Correlaciones y asociaciones categóricas son descriptivas, no causales.

## Fuentes de verdad y documentos históricos

Los informes EP3 corregido y Actividad 3.2.2 son las referencias recibidas; el primero fija el alcance y costo de diez semanas. Los modelos financieros, alternativas de arquitectura institucional y compromisos de operación anteriores se consideran retirados. Los entregables EA1/EA2 se conservan como antecedentes académicos; sus propuestas no son evidencia de implementación.
