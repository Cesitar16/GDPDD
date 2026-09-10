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

## Conflictos pendientes

- Conciliación formal del TCO Cloud entre Finanzas y Riesgos.
- Precios/cotizaciones de hardware y sizing final.
- Análisis legal/autorización y riesgo residual.
- Selección integral de arquitectura y validación clínica/local.
- El archivo `Informe_Maestro_Lucas_D1_D6_Heart_Disease.docx` estaba bloqueado por otro proceso durante esta revisión. Se utilizó su transcripción ya integrada en LaTeX; cuando quede disponible, corresponde repetir la comparación documental sin modificarlo.
- El cuaderno de resultados puede conservar salidas almacenadas de ejecuciones anteriores. Se actualizó su texto fuente de interpretación, sin reejecutar el EDA para preservar la línea base analítica vigente.

## Decisiones actualizadas

- Cloud es la preferencia financiera condicionada; la alternativa integral sigue pendiente.
- La documentación ética y los criterios CA-E01--CA-E10 están completos como línea base; las validaciones futuras no están cerradas.

## Archivos modificados

Incluye portada, resumen, discusión, conclusiones, recomendaciones, planificación, matriz de riesgos, referencias y artefactos de integración en `docs/integracion/` y `outputs/tables/`.

## Elementos que requieren confirmación del equipo

TCO de riesgos, autorización legal, aceptación de riesgos, responsables/residual y alternativa integral.

## Estado por bloque

| Bloque | Responsable | Estado | Pendiente |
|---|---|---|---|
| D1--D6 | Lucas Moncada | Línea base técnica vigente | Sizing y arquitectura integral final |
| D7--D11 | Ignacio Silva | Evaluación financiera vigente | Cotizaciones y conciliación de TCO en riesgos |
| D12--D14 | Fabián Leal | Planificación vigente como escenario Cloud base | Cobertura ética detallada y decisión integral |
| Riesgos | Vicente Hormazábal | Matriz vigente con ajuste conceptual R10 | P/I, residual y conciliación TCO |
| Ética/dataset | César Rojas | Evidencia y criterios vigentes | Validación local y desempeño futuro por subgrupos |
| Integración | Equipo | Línea base maestra preparada | Decisiones humanas pendientes |
