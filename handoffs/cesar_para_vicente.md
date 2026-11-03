# Hallazgos de datos y límites del modelo

Este registro resume evidencia verificable para la revisión de riesgos. No asigna niveles de probabilidad/impacto ni declara aceptación institucional.

| Tema | Evidencia disponible | Lectura permitida | Límite |
|---|---|---|---|
| Duplicados | 723 de 1.025 filas son duplicados exactos; quedan 302 filas únicas | Deduplicar antes de particionar evita copias exactas en ambos conjuntos | No se conoce la causa ni hay ID de paciente |
| Cobertura por sexo | 96 registros sex=0 y 206 sex=1 entre únicos | Describe desbalance de cobertura | No demuestra discriminación ni métricas diferentes |
| Edades extremas | <40: 15; 70+: 10 registros únicos | Evidencia limitada en los extremos | No permite inferencia estable por grupo |
| Intersecciones | Mujeres <40 y mujeres 70+ tienen N=5 cada una | Reportar conteos y cautela | No calcular conclusiones de equidad con N tan pequeño |
| Dominio | Dataset académico, sin muestra local | El rendimiento no se transfiere automáticamente | No hay validación poblacional local |
| Modelo | Existe un XGBoost experimental; ROC-AUC de test 0,875 | Métrica preliminar en partición de 76 casos | No es validación clínica ni evaluación suficiente por subgrupo |
| Automatización | Inferencia CSV local con ejemplos sintéticos | Prueba técnica del pipeline | No existe uso asistencial ni decisión humana registrada |

El pipeline preserva los datos originales, deduplica antes de dividir y presenta las métricas con sus límites. La evaluación por subgrupos, la validación local, la revisión clínica y los controles institucionales no se han ejecutado.
