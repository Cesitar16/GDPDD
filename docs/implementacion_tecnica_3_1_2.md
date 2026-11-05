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
- `outputs/figures/feature_engineering_delta_auc_por_fold.png`: diferencias pareadas por fold para los experimentos de interacción y splines frente a sus referencias.
- `outputs/figures/feature_engineering_repeated_cv.png`: distribución de los cambios medios por repetición en CV repetida (10 × 5 folds).
- `outputs/figures/comparacion_metricas_test_antes_despues.png`: métricas de ambos pipelines en la misma prueba retenida.
- `outputs/figures/matrices_confusion_test_comparacion.png`: conteos de errores/aciertos por clase para los dos pipelines.
- `outputs/figures/curvas_roc_test_comparacion.png`: curvas ROC de ambos pipelines en la prueba retenida.
- `outputs/figures/shap_importancia_global.png`: media de contribución absoluta TreeSHAP por variable fuente en el modelo one-hot.
- `outputs/figures/shap_relacion_valor_atribucion.png`: dirección y dispersión de contribuciones en valores numéricos/niveles categóricos observados.
- `outputs/figures/shap_explicacion_casos_error.png`: descomposición local de un falso negativo y un falso positivo del test.
- `outputs/figures/shap_importancia_comparacion.png`: comparación de las contribuciones globales del XGBoost one-hot y el baseline ordinal.
- `outputs/figures/shap_explicacion_casos_error_ordinal.png`: descomposición de los mismos errores del XGBoost ordinal, ganador de accuracy en test.
- `outputs/tables/correlacion_pearson_continuas_target.csv`, `asociacion_niveles_categoricos_target.csv` y `auditoria_extremos_iqr.csv`: cifras que respaldan los gráficos.
- `outputs/tables/matrices_confusion_test.csv`: conteos de las matrices de confusión, por modelo, clase real y predicción.
- `outputs/tables/roc_auc_cv_por_fold.csv`, `feature_engineering_delta_auc_por_fold.csv`, `feature_engineering_repeated_cv.csv` y `feature_engineering_repeated_cv_por_repeticion.csv`: resultados por fold/repetición y cambios frente a cada referencia, calculados sólo en entrenamiento.
- `outputs/tables/shap_importancia_global.csv`, `shap_contribuciones_test.csv` y `shap_casos_error_test.csv`: resumen por variable y contribuciones por fila de prueba/caso ilustrado.
- `outputs/tables/shap_importancia_global_ordinal.csv`, `shap_contribuciones_test_ordinal.csv`, `shap_casos_error_test_ordinal.csv` y `shap_importancia_comparacion.csv`: explicaciones del baseline y comparación pareada.

En la matriz Pearson sobre los 302 registros únicos, `thalach` tiene r=0,420 con target y `oldpeak` r=−0,429; la mayor correlación absoluta entre dos predictores cuantitativos es |r|=0,395 (`age` con `thalach`). Estos valores no prueban efecto causal.

## Explicabilidad del modelo seleccionado

Los dos XGBoost se explican con TreeSHAP nativo (`pred_contribs`), que descompone cada margen log-odds en un valor base y contribuciones de predictores. En el one-hot las columnas transformadas se agrupan por variable original. En el baseline ordinal se atribuyen directamente las columnas de entrada, que incluyen códigos categóricos enteros. Ambos modelos sitúan `cp`, `ca` y `thal` en los tres primeros lugares de contribución absoluta media sobre los 302 registros únicos: 0,971/0,872, 0,855/0,643 y 0,599/0,479 log-odds para one-hot/ordinal. `fbs` tiene cero en ambos artefactos. Las explicaciones locales muestran el falso negativo y el falso positivo del baseline ganador de accuracy (60/76) y los mismos casos en one-hot (59/76). La dirección se refiere sólo a las clases codificadas 1/0. SHAP describe el comportamiento de cada modelo en estos datos: no es causalidad ni importancia clínica y no demuestra la semántica de `target`.

SHAP transparenta cómo el modelo distribuye sus scores para estos registros; no revela causas, no demuestra importancia clínica ni equidad. La pequeña muestra y la semántica no verificada de `target` limitan la interpretación. Para repetir la generación, el notebook invoca `src/explainability.py` después de evaluar el modelo.

## Auditoría de todos los errores y métricas por subgrupo

El notebook `notebooks/06_auditoria_errores_y_subgrupos.ipynb` parte de las explicaciones SHAP guardadas para el mismo test; no vuelve a entrenar ni modifica la partición. Analiza los 17 errores del XGBoost one-hot: 8 falsos negativos y 9 falsos positivos. `cp`, `ca` y `thal` muestran las mayores contribuciones absolutas medias en ambos grupos de errores. Entre falsos negativos, `cp` tiene SHAP firmado promedio −0,565 log-odds y `thalach` −0,514; entre falsos positivos, `cp` promedia +0,558 y `ca` +0,566. El signo señala la dirección del score del modelo, no una causa clínica. El mapa muestra las 13 contribuciones de cada error individual y permite inspeccionar excepciones.

Se calcularon recall de `target=1` y especificidad de `target=0` para el test completo, códigos de `sex` y rangos etarios, incluyendo conteos de ambas clases e intervalos Wilson del 95 %. Para `sex=0` (n=22), recall=0,813 y especificidad=0,833; para `sex=1` (n=54), recall=0,800 y especificidad=0,724. Los intervalos son amplios y se solapan. En edades 60–69 (n=25), recall=0,500 y especificidad=0,824; en 50–59 (n=29), recall=0,778 y especificidad=0,727. Los grupos <40 y 70+ tienen sólo tres casos cada uno; no permiten conclusiones. Se marca soporte bajo cuando n<10 o una clase tiene menos de cinco casos. Estas tasas son descriptivas de una única partición: no confirman ni descartan sesgo.

La clase objetivo está relativamente equilibrada tras deduplicar (138 `target=0`, 164 `target=1`), así que no se observa un desbalance global fuerte que justifique aplicar sobremuestreo automáticamente. Aun así, `sex` tiene distinta representación y el conjunto es pequeño; esto requiere vigilancia, no permite una conclusión de equidad. El código reproducible es `src/error_bias_audit.py`; sus productos son `outputs/tables/errores_test_por_caso.csv`, `shap_resumen_errores_test.csv`, `metricas_test_por_subgrupo.csv`, y las figuras `shap_mapa_errores_test.png`, `shap_resumen_errores_test.png` y `metricas_test_por_subgrupo.png`.

## Comparación antes y después

Todos los candidatos usan la misma partición estratificada (226 train / 76 test; semilla 42). La selección se basa en ROC-AUC promedio de validación cruzada de cinco folds dentro de train. El baseline ordinal reproduce el pipeline previo; el artefacto final se selecciona entre XGBoost CUDA con codificación categórica one-hot, por la interpretación correcta de códigos categóricos y el requisito previo de usar GPU.

ROC-AUC CV: baseline XGBoost ordinal 0,917 ± 0,062; XGBoost one-hot somero 0,914 ± 0,055; XGBoost one-hot regularizado 0,913 ± 0,061. La referencia logística con RobustScaler y one-hot obtuvo 0,919 ± 0,052 en CPU. Se ensayó XGBoost con la interacción `oldpeak × exang` (0,912 ± 0,056) y logística con splines cuadráticas de tres nudos (0,904 ± 0,043). Frente a sus referencias correspondientes, el cambio medio pareado fue −0,002 y −0,015 ROC-AUC; la interacción no superó al baseline en ningún fold y las splines sólo en uno de cinco. Son experimentos exploratorios, no se incorporan al artefacto final porque no mejoraron la validación cruzada. La selección sigue restringida a candidatos XGBoost one-hot regulares y el one-hot somero fue elegido para el artefacto GPU.

Como comprobación de estabilidad se repitieron cinco folds estratificados diez veces en train. La interacción XGBoost dio 0,91262 frente a 0,91279 de media, diferencia +0,00016: mejoró en 4/10 repeticiones y empeoró en 6/10 (mediana de diferencias −0,00078; rango −0,00232 a +0,00549). La logística con splines obtuvo 0,90099 frente a 0,91897 y fue inferior en las diez repeticiones (delta medio −0,01798). Los folds repetidos comparten observaciones, por lo que estas cifras son evidencia exploratoria de estabilidad y no una prueba estadística independiente. No se seleccionó ninguna transformación experimental.

**Decisión de implementación:** no se incorporan estas transformaciones al pipeline entregado. La interacción añade una columna, pero su ganancia media es prácticamente cero y no se repite de manera consistente. Además, el XGBoost actual tiene profundidad máxima 2 y ya puede representar interacciones simples mediante divisiones sucesivas; el producto explícito no aportó una ventaja medible que justifique mantener otra transformación. Las splines aumentan los grados de libertad de la referencia logística con sólo 226 registros de entrenamiento y redujeron su ROC-AUC en las diez repeticiones. Agregar complejidad sin una mejora reproducible puede aumentar el riesgo de ajuste a peculiaridades de esta muestra y el costo de mantener el procesamiento. Se conserva el preprocesamiento actual; el resultado no prueba que toda ingeniería de variables sea inútil, sólo que estos candidatos no justifican su inclusión con la evidencia disponible.

En el conjunto test, baseline ordinal versus XGBoost one-hot seleccionado: accuracy 0,789 vs 0,776; precision clase 1 0,791 vs 0,786; recall clase 1 0,829 vs 0,805; F1 0,810 vs 0,795; ROC-AUC 0,875 vs 0,875. Las matrices de confusión son, con filas como clase real y columnas como predicción, `[[26, 9], [7, 34]]` para el baseline y `[[26, 9], [8, 33]]` para one-hot. Ambos comparten 26 verdaderos negativos y 9 falsos positivos; el baseline acierta un positivo más y comete un falso negativo menos. Su ventaja es exactamente 1/76 aciertos (1,32 puntos porcentuales), no una mejora estable demostrada. La curva ROC coincide en AUC=0,875; el pequeño cambio de accuracy ocurre en el umbral predeterminado y no cambia el AUC redondeado. La codificación one-hot conserva sentido estadístico para códigos categóricos nominales; el acierto adicional del ordinal no justifica asumir distancias/orden entre categorías. La logística CPU tuvo el mayor ROC-AUC CV, pero el artefacto seleccionado se restringió a XGBoost GPU por el requisito de ejecución acordado.

## Evaluación robusta complementaria

Además de la prueba retenida descrita arriba, `notebooks/05_evaluacion_robusta_modelo.ipynb` ejecuta validación cruzada anidada repetida para comparar selección de modelo, calibración sigmoide y umbrales sin usar los folds externos para ajustarlos. El ROC-AUC externo promedio fue 0,9112 ± 0,0104 entre medias de repetición; la calibración redujo Brier de 0,1197 a 0,1169 y log-loss de 0,3914 a 0,3745, sin alterar ROC-AUC. El umbral 0,5 tuvo balanced accuracy calibrada 0,8366; los umbrales optimizados internamente no mejoraron consistentemente esa métrica o F1. La logística fue seleccionada internamente en 14 de 15 folds, aunque el artefacto del proyecto sigue siendo XGBoost CUDA por el requisito de implementación. Estos resultados son internos y no reemplazan la prueba retenida ni constituyen validación externa. Véase [evaluación robusta](evaluacion_modelo_robusta.md) y sus tablas/figuras reproducibles.

La auditoría de fuente encontró coincidencia tabular con la publicación Kaggle declarada y documentó que `target=1` es la clase positiva según la ficha del proveedor. No se verificó clínicamente la etiqueta ni se trazaron filas a UCI; tampoco hay cohorte independiente autorizada para validación externa. El registro detallado está en `outputs/tables/auditoria_fuente_target.csv`.

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
