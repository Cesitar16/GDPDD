# Línea base maestra de integración EVA1

## 1. Proyecto y alcance

- **Decisión vigente:** piloto institucional de apoyo a la prevención cardiovascular; no es diagnóstico autónomo ni reemplaza el juicio clínico.
- **Fuente responsable:** Lucas (D1--D6), consolidada por el equipo.
- **Estado:** validado documentalmente. **Decisión de equipo:** no para este alcance; sí para cualquier ampliación clínica.

## 2. Dataset

- **Evidencia observada:** `heart.csv` contiene 1.025 filas y 14 variables; 723 filas son duplicados exactos y la versión derivada contiene 302 registros únicos.
- **Fuente responsable:** César; `data/raw/heart.csv`, `data/processed/heart_unique.csv` y EDA.
- **Estado:** validado. El dataset es académico y no representa por sí mismo una población hospitalaria chilena.

## 3. Arquitecturas

- **Cloud (GCP):** Cloud Run, Cloud SQL, Cloud Storage, IAM y Secret Manager como escenario técnico de referencia.
- **Local:** datos, procesamiento e inferencia en infraestructura hospitalaria.
- **Híbrida:** identidad y registro maestro locales; analítica controlada en GCP.
- **Decisión de cierre:** Cloud/GCP es la arquitectura integral recomendada para el piloto; Híbrida es contingencia si Cloud no supera la aprobación legal, institucional o de gobierno de datos; Local es técnicamente viable, pero no recomendado por mayor TCO y carga operacional.
- **Estado:** seleccionado de forma condicionada. **Condiciones:** CA-E01 a CA-E10, autorización y gobierno de datos aplicables, controles técnicos y de seguridad, aceptación de riesgos y validación local.

## 4. Herramientas

- Python, Pandas, NumPy, scikit-learn, PostgreSQL, SHAP, FastAPI, Streamlit, Docker y Git.
- **Estado:** decisión de diseño vigente. SHAP se utiliza para explicabilidad y revisión humana, no como demostración de equidad.

## 5. Metodología

- Enfoque adaptativo con piloto de 10 semanas y horizonte de operación/evaluación de 36 meses.
- **Estado:** supuesto de planificación vigente; el piloto no autoriza publicación automática de un modelo.

## 6. Supuestos de planificación

- 20/5, 25/6 y 30/8 usuarios/concurrencia en años 1--3; batch diario; seis ventanas semestrales; 99% operacional, RTO 8 h y RPO 24 h.
- **Volumen:** 10.000 registros históricos iniciales y 5.000 nuevos/actualizados en año 1 con 10% anual son supuestos de dimensionamiento, no resultados del EDA.

## 7. Finanzas

- **Resultado vigente de Ignacio:** TCO 36 meses Cloud CLP 10.815.487, Local CLP 16.893.013 e Híbrida CLP 15.696.956; montos de planificación con contingencia de 10%.
- **Decisión de cierre:** Cloud/GCP es la alternativa integral recomendada para el piloto. El TCO oficial Cloud es CLP 10.815.487 a 36 meses.
- **Trazabilidad histórica:** CLP 11.866.338 corresponde a una versión previa de Riesgos y no es un valor vigente. Las cotizaciones y el sizing final se confirman antes de contratación, sin alterar la línea base TCO del informe.

## 8. Ética

- **Estado:** análisis documental y criterios CA-E01 a CA-E10 completados.
- **Pendiente:** validación local, desempeño por subgrupos cuando exista modelo y N suficiente, aprobación clínica y monitoreo de deriva.

## 9. Riesgos

- R10 se basa en evidencia real de cobertura y generalización, no en los 10.000 registros de planificación. **Nivel adoptado en el informe:** P×I = 2×3 = 6 (Crítico).
- **Pendiente:** el riesgo residual no está definido y no se infiere en este informe.

## 10. EDT y Gantt

- Fabián usa Cloud/GCP como arquitectura seleccionada del piloto. Su ejecución está condicionada a los gates de cierre definidos.
- La cobertura de CA-E01--CA-E10 está documentada en `outputs/tables/cobertura_criterios_eticos_edt.csv`.

## 11. Decisiones pendientes

1. Autorización/análisis legal y gobierno de datos aplicables, sin declarar cumplimiento legal definitivo.
2. Cumplimiento verificable de CA-E01 a CA-E10, controles técnicos, de seguridad y aceptación de riesgos.
3. Cotizaciones y sizing final antes de contratación.
4. Validación clínica y local antes de cualquier uso; los umbrales clínicos no se inventan en este informe.
