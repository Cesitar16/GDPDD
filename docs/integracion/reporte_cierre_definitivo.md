# Reporte breve de cierre definitivo

## Decisiones adoptadas

- **Viabilidad:** el proyecto se declara viable condicionado.
- **Arquitectura:** Cloud/GCP es la alternativa integral recomendada para el piloto; Híbrida es contingencia ante una no aprobación legal, institucional o de gobierno de datos de Cloud; Local es técnicamente viable, pero no recomendada por mayor TCO y carga operacional.
- **Finanzas:** el TCO oficial Cloud es CLP 10.815.487 a 36 meses. El valor CLP 11.866.338 queda sólo como trazabilidad histórica de una versión previa de Riesgos.
- **R10:** se conserva la formulación basada en representación y generalización y se adopta P×I = 2×3 = 6 (Crítico). El riesgo residual no está definido.
- **Ética:** CA-E01 a CA-E10 son condiciones formales de aceptación antes del piloto.

## Condiciones previas al piloto

1. Autorización y gobierno de datos aplicables, sin declarar cumplimiento legal definitivo.
2. Cumplimiento verificable de CA-E01 a CA-E10.
3. Controles técnicos, de seguridad, continuidad y aceptación de riesgos.
4. Validación local y clínica; este informe no inventa umbrales clínicos.

## Integridad de evidencia

El dataset académico se mantiene separado del supuesto de planificación: `heart.csv` contiene 1.025 filas y 302 registros únicos deduplicados; los 10.000 registros históricos iniciales corresponden exclusivamente al dimensionamiento del piloto. No se modificaron `heart.csv`, los resultados EDA ni la evidencia primaria.

## Estado de cierre

El informe maestro queda cerrado y listo para auditoría final de rúbrica y posterior síntesis a 4--6 páginas. Las condiciones previas al piloto son gates de ejecución, no contradicciones de la línea base documental.
