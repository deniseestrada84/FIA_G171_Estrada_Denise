# Sección 5 (2.5) · Búsqueda con heurísticas: A* vs Dijkstra

**Materia:** Fundamentos de Inteligencia Artificial · Cuatrimestre 7 · Grupo 171
**Universidad:** Politécnica de Atlautla · **Docente:** Mtro. Javier García Lara
**Actividad Parcial 2 · Entrega en equipo:** 25 de octubre de 2026
**Integrantes:** Denise Estrada · Anahi Fuentes Avendaño  · Rogerio Aguilar Bello  ·  Cesar Natanael Rosales Vallejo 

## ¿Qué problema resuelve?

Encontrar la **ruta más corta (en km)** entre cabeceras municipales de la región
Amecameca – Chalco – Oriente del Valle de México (18 ciudades y 30 tramos carreteros),
por ejemplo de **Atlautla a la Ciudad de México**, y comparar dos algoritmos:

| Algoritmo | Idea | Usa heurística |
|---|---|---|
| **Dijkstra** | Expande siempre el nodo con menor costo acumulado `g(n)` | No |
| **A\*** | Expande el nodo con menor `f(n) = g(n) + h(n)` | Sí: distancia en línea recta (Haversine) |

La heurística es **admisible** (nunca sobreestima) y **consistente**, así que A\* siempre
devuelve la ruta óptima. Se verifica por código en `pruebas.py` y en `experimento.py`.

> **Nota sobre los datos:** las coordenadas son aproximadas y el costo de cada tramo es
> `distancia Haversine × factor de sinuosidad (1.15–1.45, semilla fija)`. Es un modelo académico.
> Para usar kilómetros reales, reemplaza la columna `km` de `data/aristas.csv`; el código no cambia.

## Estructura del repositorio

```
.
├── busqueda.py            # Dijkstra, A*, heurística Haversine, verificación de admisibilidad
├── experimento.py         # Experimentos: 8 casos, 306 pares, admisibilidad, escalabilidad
├── dashboard.py           # Dashboard con matplotlib (results/dashboard.png)
├── pruebas.py             # Pruebas automáticas (7 pruebas)
├── generar_datos.py       # (Opcional) regenera data/nodos.csv y data/aristas.csv
├── data/                  # nodos.csv y aristas.csv (el grafo)
├── results/               # Resultados: .json, .csv y gráficas .png
├── informe/FIA_G171_Estrada_S5.pdf   # Informe de la actividad
├── requirements.txt
└── README.md
```

## Cómo replicarlo paso a paso

Requisitos: **Python 3.10 o superior** (probado con 3.12).

1. **Clonar el repositorio**
   ```bash
   git clone https://github.com/deniseestrada84/FIA_G171_Estrada_Denise.git
   cd FIA_G171_Estrada_Denise/Seccion_5_AStar_vs_Dijkstra   # ajusta a tu carpeta
   ```
2. **(Opcional) crear entorno virtual**
   ```bash
   python -m venv .venv
   # Windows: .venv\Scripts\activate      Linux/Mac: source .venv/bin/activate
   ```
3. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```
4. **Correr las pruebas** (deben decir "Todas las pruebas pasaron")
   ```bash
   python pruebas.py
   ```
5. **Correr los experimentos** (imprime tablas y guarda `results/resultados.json` y los `.csv`)
   ```bash
   python experimento.py
   ```
6. **Generar el dashboard**
   ```bash
   python dashboard.py
   ```
   Se crea `results/dashboard.png` y una gráfica por panel (`results/fig_*.png`).

También puedes ejecutarlo en **Google Colab**: sube los archivos, ejecuta
`!pip install -r requirements.txt` y luego `!python experimento.py` y `!python dashboard.py`.

### Usar tu propio caso
```python
from busqueda import cargar_grafo, crear_heuristica, dijkstra, a_estrella
coord, grafo = cargar_grafo()
h = crear_heuristica(coord, "CDMX Centro")
print(a_estrella(grafo, "Atlautla", "CDMX Centro", h).ruta)
print(dijkstra(grafo, "Atlautla", "CDMX Centro").costo)
```

## Resultados principales

- **Ruta óptima Atlautla → CDMX Centro: 84.25 km** — Atlautla → Ozumba → Juchitepec →
  Tenango del Aire → Temamatla → Cocotitlán → Chalco → Valle de Chalco → CDMX Centro.
- A\* y Dijkstra dan **el mismo costo óptimo en los 306 pares** posibles.
- A\* **expande 33 % menos nodos en promedio** (de 0 % a 78 % según el par); en grafos
  aleatorios de 250–4000 nodos, entre 62 % y 69 % menos.
- En el grafo pequeño (18 nodos) A\* **no es más rápido en milisegundos**: calcular la heurística
  cuesta más de lo que ahorra. Con grafos grandes (≥ 2000 nodos) ambos tiempos se igualan o A\* gana.
- La heurística **2h** (A\* ponderado) **no es admisible** y dio ruta no óptima en 63 de 306 pares
  (hasta 18 % más larga), a cambio de expandir menos nodos.

