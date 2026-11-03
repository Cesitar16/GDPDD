# Evidencia de datos para planificación

Este documento comunica el estado que puede comprobarse en el repositorio. No crea hitos, fechas de avance ni asignaciones institucionales.

| Área | Trabajo verificable | Evidencia | Pendiente o límite |
|---|---|---|---|
| Calidad | Auditoría de nulos, duplicados, dominios y valores extremos | Notebook 04 y CSV en `outputs/tables/` | No se conoce identidad ni procedencia individual de las filas repetidas |
| Preparación | Deduplicación previa a la partición; codificación one-hot en modelos nuevos | `src/modeling.py` y notebook | Dominios del dataset tienen discrepancias que requieren validación de fuente |
| Modelado | Comparación de XGBoost ordinal, XGBoost one-hot y logística | Tabla de CV y métricas de test | No afirmar mejora; test N=76 |
| GPU | Entrenamiento XGBoost en CUDA | Pipeline Joblib indica `cuda:0` | Sólo evidencia entrenamiento local |
| Automatización | Inferencia por lotes para cinco filas sintéticas | `src/automatizacion_predicciones.py` y CSV de ejemplo | No API, UI, integración o despliegue |
| Ética | Límites de uso y restricciones de representación documentados | Informe maestro y matriz ética | Validación local, evaluación clínica y aprobación no realizadas |

El plan académico vigente cubre diez semanas conforme al informe EP3 corregido. La simulación del informe 3.2.2 no debe usarse como estado de avance ejecutado. Para cualquier actualización de calendario, se requiere evidencia concreta en archivos o entregables.
