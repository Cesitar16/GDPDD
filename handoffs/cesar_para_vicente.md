# Handoff de César para Vicente

> **Estado de cierre:** insumo ejecutado y conservado como trazabilidad histórica. La formulación de R10 y su nivel P×I = 2×3 = 6 (Crítico) fueron adoptados por el informe maestro; el riesgo residual no se infiere aquí.

Los riesgos siguientes fueron candidatos basados en evidencia descriptiva y en el alcance declarado. Se conservan como antecedente de la matriz integrada; el informe de cierre adopta para R10 P×I = 2×3 = 6 (Crítico) y no define riesgo residual.

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

## Alerta histórica sobre R10

La redacción histórica de R10 mencionaba “10.000 registros iniciales”. Ese número es un supuesto futuro de planificación de volumen, no el dataset analizado. La evidencia observada es **1.025 filas originales y 302 registros únicos**. El informe maestro adoptó la formulación basada en cobertura desigual por sexo, edades extremas, intersecciones pequeñas y generalización local incierta.

La propuesta histórica no modificaba la matriz integrada directamente. En el cierre, la formulación y el nivel P×I de R10 se incorporaron al informe; el riesgo residual permanece sin definir.
