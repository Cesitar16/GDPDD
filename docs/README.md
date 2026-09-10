# Documentación LaTeX EVA1

Esta carpeta contiene la documentación LaTeX modular del análisis del dataset Heart Disease. El contenido fue organizado a partir del informe maestro D1 a D6 y no modifica los archivos fuente ubicados en la raíz del proyecto.

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

El informe contiene la línea base conceptual D1 a D6, los supuestos comunes, alternativas Cloud, Local e Híbrida, stack tecnológico, metodología adaptativa, handoffs y referencias. Las figuras y tablas futuras pueden incorporarse en `figures/` y `tables/` sin alterar la estructura principal.
