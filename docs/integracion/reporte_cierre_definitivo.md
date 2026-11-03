# Estado integrado del proyecto

## Línea base

- Duración: diez semanas, 5 de octubre–13 de diciembre de 2026, conforme al EP3 corregido.
- Presupuesto de referencia: CLP 10.506.069, estimación académica para prototipo; no es gasto observado ni cotización vinculante.
- No se define operación posterior ni un presupuesto recurrente.
- La planificación 3.2.2 es un ejercicio de seguimiento con estados simulados, separado de la línea base.

## Estado técnico

El repositorio contiene un flujo de modelado y automatización de inferencia de ejemplo. El notebook elimina duplicados exactos antes de particionar, compara transformaciones en los mismos folds, evalúa en test y genera cinco predicciones sintéticas. XGBoost one-hot fue entrenado en CUDA en una RTX 4060; el pipeline y entorno están en el repo.

En test el modelo seleccionado obtuvo ROC-AUC 0,875, igual al baseline ordinal (0,875); accuracy 0,776 frente a 0,789; precisión positiva 0,786 frente a 0,791; recall 0,805 frente a 0,829; F1 0,795 frente a 0,810. Por tanto, no se documenta una mejora predictiva. La logística CPU obtuvo el mayor ROC-AUC de CV (0,919 ± 0,052), pero el artefacto GPU se conserva por requisito de implementación.

## Límites

No existe despliegue clínico, integración hospitalaria, validación con población local, calibración de scores ni aprobación clínica documentada. El dataset es pequeño y académico; el resultado es un prototipo técnico y no se debe emplear para diagnóstico, tratamiento o priorización asistencial.

Las figuras, tablas, decisiones de limpieza, pasos de reproducción y automatización se documentan en `docs/implementacion_tecnica_3_1_2.md` y en la sección de modelado del informe maestro.
