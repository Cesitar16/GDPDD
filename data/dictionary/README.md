# Diccionario de datos de Heart Disease Dataset

Este directorio documenta las 14 variables de `data/raw/heart.csv` para facilitar su uso trazable en el informe académico y en futuras etapas del proyecto.

`data/raw/heart.csv` es la fuente primaria e inmutable para los valores observados. `data/processed/heart_unique.csv` es una versión derivada para análisis de duplicados y no se utiliza como fuente del diccionario.

El archivo `diccionario_datos.csv` separa dos dimensiones: los rangos, nulos, tipos detectados y valores observados se calculan directamente desde `heart.csv`; los significados conceptuales y la codificación original se documentan a partir del repositorio UCI y de la versión publicada en Kaggle por JohnSmith88.

Se requiere cautela con `cp`, `slope`, `ca` y `thal`. Sus dominios observados no coinciden completamente con la codificación original de UCI. En particular, `ca` incluye el valor observado 4 y `thal` contiene 0--3, mientras UCI documenta 3, 6 y 7. Estos valores no se corrigen ni se eliminan: quedan registrados como advertencias documentales.

Para actualizar el diccionario, ejecute desde la raíz del repositorio:

```powershell
python src/build_data_dictionary.py
python src/build_data_dictionary.py --validate
```

El primer comando regenera el CSV y la tabla reutilizable `docs/tables/diccionario_datos.tex`; el segundo verifica filas, columnas, nombres, dominios, mínimos, máximos, nulos y valores únicos contra `heart.csv`.
