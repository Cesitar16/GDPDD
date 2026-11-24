# Tablero académico de Heart Disease

Archivo actualizado: `Heart_Disease_Tablero_Academico_Exploracion.pbix`. El archivo original se conserva sin cambios porque Windows impidió reemplazarlo desde esta sesión.

La primera página presenta el total de registros por valor observado de `target` (0 y 1). Tiene filtros de página para edad, sexo, tipo de dolor torácico (`cp`) y pendiente (`slope`), disponibles en el panel **Filtros** de Power BI.

La fuente importada es `data/raw/heart.csv`, con 1.025 filas. El gráfico cuenta registros por `target`: 499 tienen valor 0 y 526 valor 1 en esta copia del archivo.

## Lectura y límites

El informe conserva los valores codificados originales. `target` se muestra como 0/1 porque el diccionario del proyecto indica que el significado exacto de la recodificación binaria publicada no está documentado de forma concluyente. No interpretar automáticamente los valores como diagnóstico clínico individual.

Este es un análisis académico descriptivo del dataset; no constituye una herramienta clínica ni permite inferir causalidad o generalizar los resultados a una población sin considerar la representatividad del conjunto.

## Actualizar los datos

El `.pbix` tiene los datos cargados desde el CSV. Si se mueve el proyecto a otra carpeta, en Power BI Desktop se debe actualizar la ruta del origen en **Transformar datos > Configuración de origen de datos** y volver a seleccionar `data/raw/heart.csv`; luego usar **Actualizar**.
## Página de exploración

Se agregó una segunda página, **Distribuciones y muestra**, con gráficos de frecuencia por edad, tipo de dolor torácico (`cp`) y glicemia en ayunas (`fbs`). Incluye una tabla con las 14 variables para revisar registros y sus valores observados. Los filtros de página de edad, sexo, pendiente (`slope`) y tipo de dolor (`cp`) también están disponibles en esta vista.

## Página de distribución por variables

Se agregó una tercera página con seis gráficos de recuento: sexo (`sex`), electrocardiograma en reposo (`restecg`), angina inducida por ejercicio (`exang`), pendiente ST (`slope`), vasos principales (`ca`) y categoría `thal`. Los filtros de edad, sexo, `slope` y `cp` interactúan con los gráficos. Las categorías clínicas se mantienen como códigos del dataset, sin asignarles nombres o interpretaciones que no estén confirmados en el diccionario.
