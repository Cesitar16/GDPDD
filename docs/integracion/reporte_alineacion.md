# Reporte de alineación documental — revisión noviembre 2026

## Cambios incorporados

- La línea base activa se unificó en diez semanas según EP3 corregido (5 de octubre–13 de diciembre de 2026).
- Se actualizó la estimación financiera a CLP 10.506.069 para el prototipo académico. Los supuestos anteriores de TCO y operación quedan retirados.
- Se alineó la descripción de alcance: prototipo y demostración, sin despliegue ni operación institucional posterior.
- Se documentó la actividad 3.1.2, limpieza y codificación, entrenamiento CUDA, evaluación, resultados, gráficos, artefacto y automatización batch.
- Se documentó el prototipo experimental y sus métricas, sin atribuir mejora predictiva ni validez clínica.
- El informe 3.2.2 quedó identificado como ejercicio de monitoreo con estados/tareas simulados, separado del calendario EP3.

## Evidencia del modelo

- 302 filas únicas; partición 226/76; validación cruzada de cinco folds.
- ROC-AUC test 0,875 para el baseline ordinal y para el XGBoost one-hot final.
- Accuracy/precision/recall/F1: baseline 0,789/0,791/0,829/0,810; modelo final 0,776/0,786/0,805/0,795.
- Mayor ROC-AUC CV: regresión logística CPU 0,919 ± 0,052. Se conserva XGBoost por el requisito académico GPU, no por métricas superiores.
- Figuras incluidas en el informe maestro desde `outputs/figures/`.

## Límites documentados

El modelo no tiene validación local, calibración, evaluación suficiente por subgrupos, despliegue ni autorización clínica. Scores no calibrados; predicciones de ejemplo sintéticas. La guía 3.1.2 requiere copia en Google Drive; el repositorio sólo evidencia el cuaderno local.

## Fuentes de referencia

El informe EP3 corregido fija duración y presupuesto. El informe 3.2.2 aporta monitoreo y control didáctico. Los entregables EA1/EA2 y la auditoría del 6 de octubre se preservan como documentos históricos, no como línea base vigente.
