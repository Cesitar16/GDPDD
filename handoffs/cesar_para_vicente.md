# Handoff de César para Vicente

Los riesgos siguientes son candidatos basados en evidencia descriptiva y en el alcance declarado. No se asignan probabilidad, impacto, nivel, riesgo residual ni responsable definitivo: esas decisiones corresponden a Vicente y al proceso de riesgos.

| ID candidato | Riesgo candidato | Evidencia | Consecuencia potencial | Tratamiento/mitigación sugerida |
|---|---|---|---|---|
| E01 | Tratamiento insuficiente de duplicados. | 723 de 1.025 filas (70,54 %) son duplicados exactos; la causa es desconocida. | Sobreponderación de patrones y eventual contaminación entre particiones futuras. | Mantener original, documentar deduplicación y verificar separación por registro único. |
| E02 | Cobertura desigual por sexo. | Únicos: mujeres (sex=0) 96 (31,79 %); hombres (sex=1) 206 (68,21 %). | Menor evidencia para evaluar desempeño futuro en mujeres; no prueba discriminación. | Exigir evaluación por sexo con N suficiente y limitar uso sin evidencia. |
| E03 | Cobertura insuficiente de edades extremas. | Únicos: <40=15 (4,97 %); 70+=10 (3,31 %). | Generalización incierta y métricas inestables en esos rangos. | Evaluar por edad, definir N mínimo y restringir uso no respaldado. |
| E04 | Evidencia interseccional pequeña. | Mujeres <40=N5 y mujeres 70+=N5. | Porcentajes y futuras métricas no robustos para esas combinaciones. | Informar N y no aprobar uso o interpretación fuerte sin cobertura adicional. |
| E05 | Cambio de dominio Kaggle a hospital chileno. | Fuente académica externa, sin representación demostrada del sitio ni flujo local. | Desempeño/seguridad no transferibles y riesgo de generalización injustificada. | Validación local previa, documentación de población objetivo y monitoreo de deriva. |
| E06 | Desempeño desigual aún no detectado. | No hay modelo entrenado ni métricas por subgrupo. | Posibles diferencias de error que no pueden descartarse ni cuantificarse. | Evaluación por sexo/edad cuando N lo permita, reporte de limitaciones y gate ético. |
| E07 | Sesgo de automatización y daño por falsos positivos/negativos. | El proyecto prevé apoyo preventivo; no dispone de evidencia clínica validada. | Omitir revisión o tratar alertas como diagnóstico. | Human in the Loop obligatorio, protocolo de discrepancia y registro de decisiones. |
| E08 | Expansión indebida del alcance clínico. | El alcance excluye diagnóstico autónomo y decisiones clínicas automáticas. | Uso fuera del propósito preventivo y pérdida de responsabilidad humana. | Gate de alcance, mensajes de limitación y aprobación clínica antes de cualquier cambio. |
| E09 | Privacidad/gobierno insuficientes para datos de salud. | Las opciones Cloud, Local e Híbrida presentan exposiciones operacionales distintas. | Acceso indebido, uso secundario o retención sin justificación. | Minimización, pseudonimización, mínimo privilegio, propósito, retención y auditoría. |

## Alerta específica sobre R10

La redacción actual de R10 menciona “10.000 registros iniciales”. Ese número es un supuesto futuro de planificación de volumen, no el dataset analizado. La evidencia observada es **1.025 filas originales y 302 registros únicos**. Se propone que Vicente reemplace la evidencia de R10 por una formulación como: “La cobertura del dataset analítico deduplicado es desigual por sexo y limitada en edades extremas e intersecciones (302 registros únicos); si se desarrolla un modelo sin validación por subgrupos y datos locales, podrían aparecer resultados no generalizables”.

Vicente debe decidir si lo conserva, descompone en riesgos separados o lo reemplaza; también define P/I, nivel, responsables, mitigación definitiva y riesgo residual. Esta propuesta no modifica la matriz integrada de riesgos directamente.
