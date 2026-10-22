# Sección 3. Búsqueda Local: Hill Climbing y Simulated Annealing

**Asignatura:** Fundamentos de Inteligencia Artificial  
**Universidad:** Universidad Politécnica de Atlautla  
**Carrera:** Ingeniería en Tecnologías de la Información e Innovación Digital  
**Grupo:** 171  
**Tema:** 2.3 Búsqueda Local  
**Alumna:** Denise Estrada Franco  
**Fecha de entrega:** 22 de octubre de 2026

## 1. Descripción del proyecto

Este proyecto implementa y compara dos algoritmos de búsqueda local para resolver una versión del problema del viajante de comercio (*Traveling Salesman Problem*, TSP). El objetivo es encontrar una ruta que visite 18 ciudades exactamente una vez y regrese a la ciudad de origen, minimizando la distancia total.

Las distancias geográficas aproximadas se calculan con la fórmula de Haversine. Se implementan Hill Climbing y Simulated Annealing con vecindad 2-opt, y se utiliza Held-Karp como referencia exacta.

## 2. Tecnologías y requisitos

- Python 3
- NumPy
- Matplotlib
- Pillow (para guardar las animaciones GIF)

Instala las dependencias con:

```bash
python -m pip install numpy matplotlib pillow
```

## 3. Estructura del proyecto

```text
S3_Busqueda_Local/
├── README.md
├── FIA_G171_Estrada_S3.pdf     # informe en PDF
├── busqueda_local.py
├── resultados.json             # se genera al ejecutar el programa
└── figuras/
    ├── convergencia.png
    ├── sa_actual_vs_mejor.png
    ├── rutas.png
    ├── comparacion.png
    ├── sensibilidad.png
    ├── animacion_hill_climbing.gif
    └── animacion_simulated_annealing.gif
```

Las imágenes se generan al ejecutar el programa.
el archivo JSON ya está incluido en esta carpeta con los resultados de la entrega. Se vuelven a generar (y se sobrescriben) cada vez que se ejecuta el programa.

## 4. Cómo ejecutar

Descarga o clona el repositorio, abre una terminal dentro de la carpeta `S3_Busqueda_Local` y ejecuta:

```bash
python busqueda_local.py
```

El programa ejecuta los experimentos, guarda métricas en `resultados.json`, crea cinco gráficas estáticas y genera dos animaciones GIF. La ejecución completa puede tardar varios minutos, dependiendo del equipo, porque incluye múltiples corridas y el cálculo de referencia exacta.

## 5. Animaciones

- **`figuras/animacion_hill_climbing.gif`:** muestra cómo cambia la ruta aceptada por Hill Climbing y cómo evoluciona su costo durante las iteraciones.
- **`figuras/animacion_simulated_annealing.gif`:** muestra la ruta actual, la mejor ruta encontrada y la evolución del costo actual y del mejor costo de Simulated Annealing.

Las animaciones guardan un cuadro cada 500 iteraciones para que los archivos sean más ligeros. No se requiere una ventana interactiva: los GIF se guardan en la carpeta `figuras/`.

## 6. Parámetros principales

| Parámetro | Valor |
|---|---:|
| Número de ciudades | 18 |
| Iteraciones por corrida principal | 20,000 |
| Corridas por algoritmo | 30 |
| Temperatura inicial de Simulated Annealing | 300 km |
| Factor de enfriamiento | 0.9995 |
| Vecindad | 2-opt |

También se realizan experimentos de sensibilidad con diferentes temperaturas iniciales, factores de enfriamiento y números de iteraciones.

## 7. Resultados generados

- `resultados.json`: métricas estadísticas, rutas, tiempos de ejecución y resultados de sensibilidad.
- `figuras/convergencia.png`: evolución del costo durante las iteraciones.
- `figuras/sa_actual_vs_mejor.png`: costo actual y mejor costo de Simulated Annealing.
- `figuras/rutas.png`: comparación de las rutas finales de ambos métodos y de la referencia exacta.
- `figuras/comparacion.png`: distribución de los costos finales.
- `figuras/sensibilidad.png`: efecto de los parámetros de Simulated Annealing.
- `figuras/animacion_hill_climbing.gif`: animación de la ruta y convergencia de Hill Climbing.
- `figuras/animacion_simulated_annealing.gif`: animación de la ruta actual, la mejor ruta y la convergencia de Simulated Annealing.

## 8. Evaluación

Los algoritmos se comparan mediante el mejor, peor y costo medio de las rutas, mediana, desviación estándar, número de corridas que alcanzan el óptimo de referencia, tiempo de ejecución, convergencia y sensibilidad a los parámetros.

## 9. Limitaciones

Las distancias son aproximaciones geográficas en línea recta y no distancias reales por carretera. Los resultados dependen de las semillas y de los parámetros. Held-Karp permite obtener una referencia exacta para este tamaño del problema, pero su costo computacional crece rápidamente al aumentar el número de ciudades.

