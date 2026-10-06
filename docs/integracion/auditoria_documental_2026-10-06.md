# Auditoría documental y plan de integración

Fecha de revisión: 6 de octubre de 2026.

## Alcance de la auditoría

Se revisaron la línea base del informe maestro, las actividades EA2 ya integradas y dos documentos de referencia entregados para este trabajo. Las referencias se usaron para identificar prácticas transferibles de gestión, trazabilidad, costos, riesgos, marcos de trabajo, roles e indicadores. No se trasladan al proyecto los supuestos de e-commerce, LLM, precios en USD ni KPI propios del chatbot.

## Hallazgos de coherencia

La línea base es consistente en los puntos principales: apoyo preventivo sin diagnóstico autónomo; dataset académico de 1.025 filas con 723 duplicados exactos y 302 registros únicos; piloto de 10 semanas separado de la operación evaluada a 36 meses; TCO Cloud de CLP 10.815.487; y selección condicionada de Cloud/GCP, con Híbrida como contingencia.

Se identificaron brechas de consolidación, no contradicciones: la relación entre PMBOK, Scrum y CRISP-DM no estaba explicitada en el informe maestro; los requisitos EA2 no estaban enlazados centralmente con EDT y gates; faltaba una matriz operativa de indicadores, una RACI/cadencia de comunicación y un tablero único de aceptación.

## Decisiones de integración

- PMBOK se aplica al gobierno y a la documentación: alcance, interesados, cronograma, costos, riesgos, comunicaciones, calidad y control de cambios.
- Scrum se aplica al desarrollo del piloto mediante cinco sprints de dos semanas, con backlog, objetivos de sprint, revisiones y retrospectivas.
- CRISP-DM se aplica a las actividades técnicas de datos. Puede iterar dentro de los sprints cuando la evidencia lo exija.
- MLOps no se declara implantado: queda como capacidad futura condicionada a continuidad, autorización y madurez operacional.
- Los KPI clínicos y los umbrales de modelos se mantienen pendientes de acuerdo con la contraparte clínica; no se infieren a partir del dataset académico.

## Archivos incorporados

- `docs/sections/23_gobernanza_y_ejecucion.tex`: definición de marcos, Scrum, RACI y comunicaciones.
- `docs/sections/24_requisitos_indicadores_y_aceptacion.tex`: requisitos, indicadores, gates y tratamiento documental del riesgo residual.

## Validación pendiente

Antes de considerar una entrega cerrada se debe compilar y revisar visualmente el informe maestro actualizado. La auditoría inicial detectó avisos de tablas anchas en anexos existentes; deben revisarse en la siguiente validación de renderizado. La compilación integrada de Codex no estuvo disponible durante esta revisión por una limitación de directorios de plataforma, no por un diagnóstico del contenido LaTeX.
