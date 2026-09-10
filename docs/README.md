# Documentación LaTeX EVA1

Esta carpeta contiene la documentación LaTeX modular del informe maestro integrado del proyecto Heart Disease. Integra D1--D14, riesgos, ética, dataset y trazabilidad sin modificar los archivos fuente ubicados en la raíz del proyecto.

## Compilación

Desde esta carpeta, ejecute:

```powershell
pdflatex -output-directory=build main.tex
biber --output-directory build main
pdflatex -output-directory=build main.tex
pdflatex -output-directory=build main.tex
```

El PDF resultante queda en `build/main.pdf`. Las figuras se organizan por análisis en `figures/` y las tablas editables pueden mantenerse en `tables/`.

## Alcance del documento

El informe contiene la línea base técnica, evaluación financiera, planificación, riesgos, ética/dataset, alternativas Cloud, Local e Híbrida, trazabilidad y referencias. La documentación de consistencia y cierre se encuentra en `integracion/`; las tablas de alineación reutilizables se encuentran en `../outputs/tables/`.
