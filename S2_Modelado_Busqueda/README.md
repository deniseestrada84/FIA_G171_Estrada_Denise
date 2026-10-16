# Sección 2. Problemas de búsqueda y espacios de búsqueda

**Asignatura:** Fundamentos de Inteligencia Artificial\
**Universidad:** Politécnica de Atlautla\
**Programa educativo:** Ingeniería en Tecnologías de la Información e
Innovación Digital 
**Grupo:** 171
**Docente:** Mtro. Javier García Lara\
**Estudiante:** Denise Estrada Franco\
**Fecha de entrega:** 18 de octubre de 2026

------------------------------------------------------------------------

## 1. Descripción del proyecto

Este proyecto modela dos problemas como espacios de búsqueda mediante
Python y NetworkX:

1.  **Red de calles:** representa una red de intersecciones conectadas
    mediante arcos dirigidos y ponderados. Los pesos indican el tiempo
    estimado de recorrido en minutos.
2.  **Robot de almacén:** representa el desplazamiento de un robot en
    una cuadrícula de 4 × 4 celdas con obstáculos. El robot puede
    moverse hacia el norte, sur, este y oeste cuando la celda de destino
    es válida.

El programa construye y visualiza los grafos, genera estados sucesores y
aplica el algoritmo de Dijkstra para encontrar la ruta de menor coste en
la red de calles.

## 2. Requisitos

-   Python 3.8 o superior.
-   NetworkX.
-   Matplotlib.

## 3. Instalación

Abre una terminal en la carpeta del proyecto e instala las bibliotecas
necesarias:

``` bash
python -m pip install networkx matplotlib
```

En Windows, si utilizas el lanzador `py`, puedes ejecutar:

``` bash
py -m pip install networkx matplotlib
```
## 4. Ejecución

1.  Descarga o clona el repositorio.
2.  Abre una terminal dentro de la carpeta del proyecto.
3.  Instala las bibliotecas indicadas en la sección 3.
4.  Ejecuta el archivo Python:

``` bash
python 2problemasS2.py
```

En Windows también puedes utilizar:

``` bash
py 2problemasS2.py
```

5.  Revisa la información que aparece en la consola y los diagramas
    generados en la carpeta de ejecución.

## 5. Funciones principales

  -----------------------------------------------------------------------
  Función                             Descripción
  ----------------------------------- -----------------------------------
  `crear_grafo_calles()`              Construye el grafo dirigido y
                                      ponderado de la red de calles.

  `generador_estados_calles()`        Obtiene los estados sucesores y el
                                      coste de las transiciones desde una
                                      intersección.

  `encontrar_ruta_optima()`           Utiliza Dijkstra para calcular la
                                      ruta de menor coste y su coste
                                      total.

  `dibujar_grafo_calles()`            Genera la visualización de la red
                                      de calles y resalta la ruta óptima.

  `es_valido()`                       Comprueba si una celda del almacén
                                      está dentro de los límites y libre
                                      de obstáculos.

  `generador_estados_robot()`         Genera los movimientos válidos del
                                      robot.

  `crear_grafo_robot()`               Construye el grafo de los estados
                                      alcanzables del robot.

  `dibujar_grafo_robot()`             Genera la visualización del espacio
                                      de estados del robot.
  -----------------------------------------------------------------------

Los nombres anteriores describen las funciones previstas en el código;

## 6. Resultados esperados

### Problema 1. Red de calles

-   Nodos: 7.
-   Arcos dirigidos: 11.
-   Estado inicial: A, restaurante.
-   Estado meta: G, cliente.
-   Ruta de menor coste obtenida con Dijkstra: **A → C → D → G**.
-   Coste total de la ruta: **7 minutos**.

El coste se obtiene sumando los pesos de los arcos de la ruta: 2 + 1 + 4
= 7 minutos.

### Problema 2. Robot de almacén

-   Cuadrícula: 4 × 4 celdas.
-   Estados alcanzables previstos: 13.
-   Arcos dirigidos previstos: 32.
-   Estado inicial: (0, 0).
-   Estado meta: (3, 2).
-   Coste por movimiento: 1.


## 7. Análisis de complejidad

Para un grafo con (n) nodos y (m) arcos, la construcción y el recorrido
básico del grafo pueden analizarse en función de (n + m). La complejidad
concreta de Dijkstra depende de la implementación y de la estructura de
datos utilizada. En el proyecto, el espacio de estados es pequeño, por
lo que los grafos pueden visualizarse y analizarse de manera directa.

