# Reporte de alineación e integración

## Conflictos detectados

- La portada describía sólo D1--D6 y a Lucas, aunque el informe maestro integra D1--D14, riesgos y ética.
- R10 atribuía el riesgo de representación a 10.000 registros de planificación y trataba SHAP como mitigación de sesgo.
- La matriz de riesgos conserva TCO Cloud CLP 11.866.338; la evaluación financiera formal de Ignacio documenta CLP 10.815.487.
- Discusión y recomendaciones presentaban como pendientes la preferencia financiera y el análisis ético ya documentados.
- Algunos metadatos EDA aún indicaban que la codificación de `sex` no estaba documentada; el diccionario/UCI la respalda.
- La EDT utiliza GCP como base de planificación y requería explicitar que no cierra la decisión integral.

## Conflictos corregidos

- Identidad del informe maestro y terminología de estados.
- Separación explícita entre dataset académico observado y supuesto de volumen del piloto.
- Redacción conceptual de R10 y del uso de SHAP, preservando la autoridad de Vicente sobre P/I y residual.
- Referencias internas de finanzas, ética y planificación actualizadas a su estado vigente.
- Codificación UTF-8 corregida en las referencias internas afectadas.

## Condiciones de ejecución pendientes

- Precios/cotizaciones de hardware y sizing final.
- Análisis legal/autorización y gobierno de datos aplicables; no se declara cumplimiento legal definitivo.
- Riesgo residual de R10, si el equipo decide definirlo.
- Cumplimiento verificable de CA-E01 a CA-E10 y validación clínica/local antes del piloto.
- El archivo `Informe_Maestro_Lucas_D1_D6_Heart_Disease.docx` estaba bloqueado por otro proceso durante esta revisión. Se utilizó su transcripción ya integrada en LaTeX; cuando quede disponible, corresponde repetir la comparación documental sin modificarlo.
- El cuaderno de resultados puede conservar salidas almacenadas de ejecuciones anteriores. Se actualizó su texto fuente de interpretación, sin reejecutar el EDA para preservar la línea base analítica vigente.

## Decisiones de cierre

- TCO oficial Cloud: CLP 10.815.487 a 36 meses; CLP 11.866.338 queda sólo como trazabilidad histórica.
- El proyecto es viable condicionado. Cloud/GCP queda recomendada para el piloto; Híbrida es contingencia y Local no se recomienda para este piloto.
- R10 adopta P×I = 2×3 = 6 (Crítico); el riesgo residual no está definido.
- La documentación ética y los criterios CA-E01--CA-E10 son condiciones formales de aceptación; las validaciones futuras no están cerradas.

## Archivos modificados

Incluye portada, resumen, discusión, conclusiones, recomendaciones, planificación, matriz de riesgos, referencias y artefactos de integración en `docs/integracion/` y `outputs/tables/`.

## Elementos que requieren confirmación del equipo

Autorización legal y gobierno de datos, cumplimiento de gates, aceptación de riesgos, riesgo residual de R10, cotizaciones/sizing y validación local.

## Estado por bloque

| Bloque | Responsable | Estado | Pendiente |
|---|---|---|---|
| D1--D6 | Lucas Moncada | Línea base técnica vigente | Sizing antes de contratación |
| D7--D11 | Ignacio Silva | TCO Cloud oficial CLP 10.815.487 | Cotizaciones/sizing antes de contratación |
| D12--D14 | Fabián Leal | Cloud/GCP seleccionado para piloto condicionado | Ejecución sólo tras gates previos |
| Riesgos | Vicente Hormazábal | R10 formulado con P×I = 2×3 = 6 | Riesgo residual, si corresponde |
| Ética/dataset | César Rojas | Evidencia y criterios vigentes | Validación local y desempeño futuro por subgrupos |
| Integración | Equipo | Informe maestro cerrado como viable condicionado | Auditoría de rúbrica y síntesis posterior |
