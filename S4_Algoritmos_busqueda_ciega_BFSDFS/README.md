# Fundamentos de Inteligencia Artificial · Actividad Parcial 2 · Sección 4

**BFS y DFS para resolver un laberinto (tema 2.4: algoritmos de búsqueda ciega)**  
Universidad Politécnica de Atlautla · Ingeniería en Tecnologías de la Información e Innovación Digital  
Docente: Mtro. Javier García Lara · Grupo 171 · Cuatrimestre 7

Este README explica el objetivo del proyecto, los requisitos, la instalación, la ejecución y la interpretación de los resultados.

---

## 1. ¿De qué trata el proyecto?

El laberinto se representa como un **grafo**: cada celda libre es un nodo y cada par de celdas libres adyacentes es una arista. Se busca un camino desde la entrada `(1, 1)` hasta la salida `(n-2, n-2)` mediante dos algoritmos de búsqueda ciega:

| Característica | BFS (búsqueda en anchura) | DFS (búsqueda en profundidad) |
|---|---|---|
| Estrategia | Explora por niveles, desde los estados más cercanos al inicio | Profundiza por una rama y retrocede cuando es necesario |
| Frontera | Cola FIFO | Pila LIFO |
| Operación en Python | `popleft()` | `pop()` |
| Camino | Encuentra un camino mínimo si cada movimiento cuesta lo mismo | Encuentra un camino, pero no garantiza que sea el más corto |

El programa compara los algoritmos en laberintos de `11×11`, `21×21`, `31×31`, `41×41` y `61×61`, tanto perfectos (sin ciclos) como con lazos (con ciclos). Registra longitud del camino, nodos expandidos, tamaño máximo de la frontera y tiempo de ejecución.

---

## 2. Requisitos

- **Python 3.10 o superior**.
- **Visual Studio Code** es recomendable, pero no obligatorio.
- Bibliotecas: `networkx`, `matplotlib`, `numpy` y `pillow` (Pillow se usa para guardar la animación GIF).

Comprueba la versión de Python desde una terminal:

```bash
python --version
```

En Windows, si el comando anterior no funciona, prueba:

```bash
py --version
```

---

## 3. Instalación y ejecución

### Paso 1. Prepara la carpeta

Coloca estos archivos en una misma carpeta:

- `busqueda_ciega_laberinto.py`
- `animacion_bfs_dfs.py`
- `requirements.txt`

### Paso 2. Abre la carpeta en Visual Studio Code

Selecciona **Archivo > Abrir carpeta...** y elige la carpeta del proyecto.

### Paso 3. Abre una terminal

Selecciona **Terminal > Nueva terminal**.

### Paso 4. Instala las bibliotecas

Ejecuta una sola vez:

```bash
python -m pip install -r requirements.txt
```

Si en Windows usas el lanzador `py`, también puedes ejecutar:

```bash
py -m pip install -r requirements.txt
```

### Paso 5. Ejecuta el programa principal

```bash
python busqueda_ciega_laberinto.py
```

En Windows, si es necesario:

```bash
py busqueda_ciega_laberinto.py
```

El programa imprime resultados y crea la carpeta `resultados/` con los archivos de salida.

### Paso 6. Genera la animación (opcional)

Cuando el programa principal ya esté en la carpeta, ejecuta:

```bash
python animacion_bfs_dfs.py
```

Se guardará `resultados/animacion_bfs_dfs.gif`. Puedes abrirlo con un navegador o una aplicación que reproduzca GIF.

---

## 4. Archivos de salida

Al ejecutar el programa principal, se generan estos archivos dentro de `resultados/`:

| Archivo | Contenido |
|---|---|
| `resultados_semilla42.csv` | Resultados para los tamaños y tipos de laberinto usando la semilla 42 |
| `promedios_30_semillas.csv` | Promedios de 30 semillas por cada configuración |
| `fig_bfs.png` y `fig_dfs.png` | Ruta y nodos explorados por cada algoritmo en un laberinto de `21×21` con lazos |
| `fig_grafo9.png` | Grafo de un laberinto pequeño de `9×9`, con las rutas de BFS y DFS |
| `fig_comparacion.png` | Gráficas comparativas generadas por el programa |
| `demo9.txt` | Representación textual del laberinto pequeño (`#` = pared, `.` = celda libre) |
| `animacion_bfs_dfs.gif` | Animación opcional; solo aparece después de ejecutar `animacion_bfs_dfs.py` |

### Colores de las figuras y de la animación

| Color | Significado |
|---|---|
| Naranja | Nodo explorado |
| Azul claro | Nodo pendiente en la cola o la pila |
| Morado | Nodo que se está procesando |
| Azul oscuro | Camino final |
| Verde | Entrada |
| Rojo | Salida |

### Interpretación de los resultados

BFS garantiza un camino mínimo cuando todos los movimientos tienen el mismo costo. En un laberinto perfecto, la ruta entre la entrada y la salida es única, por lo que BFS y DFS deben devolver rutas de la misma longitud. En laberintos con ciclos, la longitud de la ruta y el número de nodos expandidos dependen de la estructura del laberinto y del orden de exploración; DFS **no garantiza** un camino mínimo.

Como ejemplo registrado en el informe para un laberinto de `21×21` con lazos y semilla 42: BFS encuentra un camino de 92 pasos y expande 198 nodos; DFS encuentra un camino de 144 pasos y expande 176 nodos. Si los resultados cambian, verifica que estés usando la misma versión del código y las mismas semillas. Los tiempos pueden variar según el equipo y la carga del sistema.

---

## 5. Cómo modificar los experimentos

En `busqueda_ciega_laberinto.py`, dentro de `main()`, se encuentran estos parámetros:

```python
tamaños = [11, 21, 31, 41, 61]
tipos = {"perfecto": 0.0, "con_lazos": 0.10}
SEED = 42
N_SEMILLAS = 30
```

- `tamaños`: dimensiones de los laberintos; deben ser números impares.
- `tipos`: proporción de paredes internas que se abren para crear lazos.
- `SEED`: semilla para los resultados principales.
- `N_SEMILLAS`: número de laberintos usados para calcular los promedios.

En `animacion_bfs_dfs.py`, la función principal permite modificar los parámetros:

```python
def main(n=21, semilla=42, lazos=0.10, paso=2, pausa=25):
```

`n` es el tamaño del laberinto, `semilla` controla su generación, `lazos` indica la proporción de paredes que se abren, `paso` determina cuántos nodos avanza cada cuadro y `pausa` controla los cuadros adicionales al final de la animación.

---

## 6. Solución de problemas frecuentes

| `ModuleNotFoundError: No module named 'busqueda_ciega_laberinto'` | El archivo de animación no encuentra el programa principal | Coloca ambos archivos `.py` en la misma carpeta y conserva sus nombres |
| `ModuleNotFoundError` para `networkx`, `matplotlib` o `numpy` | Faltan bibliotecas | Ejecuta `python -m pip install -r requirements.txt` |
| Error al guardar el GIF o falta `PIL` | Pillow no está instalado | Ejecuta `python -m pip install pillow` o instala de nuevo `requirements.txt` |
| `pip` no se reconoce | Python o pip no está disponible en el PATH | Prueba `py -m pip install -r requirements.txt` |
| La animación no aparece | No se ejecutó el archivo opcional o se revisó otra carpeta | Ejecuta `python animacion_bfs_dfs.py` y revisa `resultados/animacion_bfs_dfs.gif` |
| Los tiempos en milisegundos difieren de los del informe | El rendimiento depende del equipo y de la carga del sistema | Es normal; vuelve a ejecutar varias veces. Los pasos y nodos deben compararse usando los mismos datos y el mismo código |
