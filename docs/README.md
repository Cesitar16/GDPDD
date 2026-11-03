# Documentación LaTeX EVA1

Esta carpeta contiene la documentación LaTeX modular del informe maestro del proyecto Heart Disease. La línea base vigente comprende diez semanas y un prototipo académico. El informe integra planificación, estado del dataset, modelo experimental, gráficos, resultados y límites de uso.

El documento autónomo `modelo.tex` concentra la documentación técnica del modelo: diccionario y tipos de variables, auditoría y preparación de datos, correlaciones, entrenamiento GPU, validación, métricas, gráficos, reproducibilidad y limitaciones. Su PDF se genera como `build/modelo.pdf`.

## Compilación

Desde esta carpeta, ejecute:

```powershell
pdflatex -output-directory=build main.tex
biber --output-directory build main
pdflatex -output-directory=build main.tex
pdflatex -output-directory=build main.tex
```

El PDF resultante queda en `build/main.pdf`. Las figuras se organizan por análisis en `figures/` y las tablas editables pueden mantenerse en `tables/`.

Para compilar el informe independiente del modelo desde esta carpeta:

```powershell
latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=build modelo.tex
```

## Alcance del documento

El informe contiene la línea base técnica, evaluación financiera, planificación, riesgos, ética/dataset, alternativas Cloud, Local e Híbrida, trazabilidad y referencias. La documentación de consistencia y cierre se encuentra en `integracion/`; las tablas de alineación reutilizables se encuentran en `../outputs/tables/`.
