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
- **Fuente responsable:** Lucas. **Estado:** alternativas comparables; la selección integral sigue pendiente de decisión de equipo.

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
- **Decisión vigente:** Cloud es la alternativa financieramente preferida, condicionada a ética, legalidad y riesgos.
- **Pendiente:** conciliar con la fuente de riesgos que conserva CLP 11.866.338; respaldo documental de hardware y precios finales.

## 8. Ética

- **Estado:** análisis documental y criterios CA-E01 a CA-E10 completados.
- **Pendiente:** validación local, desempeño por subgrupos cuando exista modelo y N suficiente, aprobación clínica y monitoreo de deriva.

## 9. Riesgos

- La matriz de Vicente mantiene la escala P×I y responsables. R10 debe basarse en la evidencia real de cobertura y generalización, no en los 10.000 registros de planificación.
- **Pendiente:** Vicente valida P/I, nivel y riesgo residual; Ignacio y Vicente concilian la línea base TCO.

## 10. EDT y Gantt

- Fabián usa Cloud como escenario base de planificación por la preferencia financiera. Esto no determina la recomendación integral definitiva.
- La cobertura de CA-E01--CA-E10 está documentada en `outputs/tables/cobertura_criterios_eticos_edt.csv`.

## 11. Decisiones pendientes

1. Recomendación integral de arquitectura.
2. Autorización/análisis legal y gobierno de datos aplicable.
3. Conciliación TCO entre Finanzas y Riesgos.
4. Cotizaciones y sizing final.
5. Validación clínica y local antes de cualquier uso.
