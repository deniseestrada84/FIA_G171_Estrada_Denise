"""
Animacion OPCIONAL: BFS y DFS explorando el mismo laberinto, lado a lado.

Sirve para ENTENDER la diferencia entre los dos algoritmos viendolos "moverse".
No es obligatoria para la actividad; el informe usa las imagenes fijas.

Uso (con busqueda_ciega_laberinto.py en la misma carpeta):
    python animacion_bfs_dfs.py
Genera: resultados/animacion_bfs_dfs.gif
"""
import os
from collections import deque

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation, PillowWriter
from matplotlib.colors import to_rgb

from busqueda_ciega_laberinto import (OUT, adyacencia, bfs, dfs, generar_laberinto,
                                      laberinto_a_grafo)

# Colores
PARED = to_rgb("#2b2b2b")
LIBRE = to_rgb("#ffffff")
VISITADO = to_rgb("#f6c177")    # ya explorado (expandido)
FRONTERA = to_rgb("#7ec8e3")    # esta en la cola/pila: pendiente de visitar
ACTUAL = to_rgb("#9b2fae")      # nodo que se esta expandiendo ahora
CAMINO = to_rgb("#1f3f8f")      # camino final


def trazar_bfs(ady, ini, meta):
    """Misma logica que bfs(), pero guarda en cada paso (nodo, frontera)."""
    frontera = deque([ini])
    padre = {ini: None}
    pasos = []
    while frontera:
        nodo = frontera.popleft()            # sale el MAS ANTIGUO (cola)
        if nodo != meta:
            for v in ady[nodo]:
                if v not in padre:
                    padre[v] = nodo
                    frontera.append(v)
        pasos.append((nodo, list(frontera)))
        if nodo == meta:
            break
    return pasos


def trazar_dfs(ady, ini, meta):
    """Misma logica que dfs(), pero guarda en cada paso (nodo, frontera)."""
    frontera = [(ini, None)]
    visitados = set()
    pasos = []
    while frontera:
        nodo, _ = frontera.pop()             # sale el MAS NUEVO (pila)
        if nodo in visitados:
            continue
        visitados.add(nodo)
        if nodo != meta:
            for v in reversed(ady[nodo]):
                if v not in visitados:
                    frontera.append((v, nodo))
        pendientes = {n for n, _ in frontera if n not in visitados}
        pasos.append((nodo, list(pendientes)))
        if nodo == meta:
            break
    return pasos


def main(n=21, semilla=42, lazos=0.10, paso=2, pausa=25):
    os.makedirs(OUT, exist_ok=True)
    g = generar_laberinto(n, semilla, lazos)
    G = laberinto_a_grafo(g)
    ady = adyacencia(G)
    ini, meta = (1, 1), (n - 2, n - 2)

    algoritmos = []
    for nombre, trazar, resolver in (("BFS (cola)", trazar_bfs, bfs), ("DFS (pila)", trazar_dfs, dfs)):
        pasos = trazar(ady, ini, meta)
        camino, expandidos, _, orden = resolver(ady, ini, meta)
        # la animacion debe mostrar EXACTAMENTE lo mismo que el codigo del informe
        assert [p[0] for p in pasos] == orden
        algoritmos.append({"nombre": nombre, "pasos": pasos, "camino": camino})

    base = np.zeros((n, n, 3))
    for r in range(n):
        for c in range(n):
            base[r, c] = PARED if g[r][c] else LIBRE

    def pintar(alg, k):
        img = base.copy()
        pasos = alg["pasos"]
        for nodo, _ in pasos[:k]:
            img[nodo] = VISITADO
        for nodo in pasos[k - 1][1]:
            img[nodo] = FRONTERA
        if k == len(pasos):
            for nodo in alg["camino"]:
                img[nodo] = CAMINO
        img[pasos[k - 1][0]] = ACTUAL
        img[ini] = to_rgb("#2e9e4f")
        img[meta] = to_rgb("#d62728")
        return img

    fig, axs = plt.subplots(1, 2, figsize=(8.4, 4.9))
    ims = []
    for ax, alg in zip(axs, algoritmos):
        ims.append(ax.imshow(pintar(alg, 1), interpolation="nearest"))
        ax.axis("off")
    fig.text(0.5, 0.025,
             "naranja = ya explorado   |   azul claro = pendiente (en la cola/pila)   |   "
             "morado = nodo actual   |   azul oscuro = camino final",
             ha="center", fontsize=7.5)
    fig.tight_layout(rect=(0, 0.05, 1, 1))

    total = max(len(a["pasos"]) for a in algoritmos)
    n_frames = (total + paso - 1) // paso + pausa

    def actualizar(f):
        for ax, im, alg in zip(axs, ims, algoritmos):
            k = min((f + 1) * paso, len(alg["pasos"]))
            im.set_data(pintar(alg, k))
            if k == len(alg["pasos"]):
                ax.set_title(f"{alg['nombre']}: llegó a la salida\n"
                             f"{k} nodos expandidos, camino de {len(alg['camino']) - 1} pasos",
                             fontsize=9, color="#1f3f8f")
            else:
                ax.set_title(f"{alg['nombre']}\nnodos expandidos: {k}", fontsize=9)
        return ims

    anim = FuncAnimation(fig, actualizar, frames=n_frames, interval=100)
    salida = os.path.join(OUT, "animacion_bfs_dfs.gif")
    anim.save(salida, writer=PillowWriter(fps=10), dpi=75)
    plt.close(fig)
    print("GIF guardado en", salida, f"({n_frames} cuadros)")


if __name__ == "__main__":
    main()