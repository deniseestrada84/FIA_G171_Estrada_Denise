"""
Actividad Parcial 2 - Seccion 4 (2.4 Algoritmos de busqueda ciega: BFS / DFS)
Fundamentos de Inteligencia Artificial - Universidad Politecnica de Atlautla

Problema: encontrar un camino de la entrada a la salida de un laberinto.
- El laberinto se modela como un grafo no dirigido (networkx): cada celda libre
  es un nodo y cada par de celdas libres adyacentes es una arista de costo 1.
- BFS y DFS estan implementados a mano (sin usar los de networkx) y se validan
  contra networkx.shortest_path_length.

Uso:
    python busqueda_ciega_laberinto.py            # corre todo y guarda resultados en ./resultados
"""
import csv
import os
import random
import statistics
import time
from collections import deque

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.colors import ListedColormap

# Orden fijo de vecinos (arriba, derecha, abajo, izquierda) para que los
# resultados sean reproducibles.
MOVES = [(-1, 0), (0, 1), (1, 0), (0, -1)]
OUT = "resultados"


# ----------------------------------------------------------------------------
# 1. Generacion de laberintos (0 = libre, 1 = pared)
# ----------------------------------------------------------------------------
def generar_laberinto(n, seed, lazos=0.0):
    """Laberinto n x n (n impar) con backtracker recursivo (iterativo).
    lazos = fraccion de paredes internas que se derriban despues para crear
    ciclos (laberinto 'con lazos'); con 0.0 es un laberinto perfecto (arbol)."""
    rng = random.Random(seed)
    g = [[1] * n for _ in range(n)]
    g[1][1] = 0
    pila = [(1, 1)]
    while pila:
        r, c = pila[-1]
        opciones = []
        for dr, dc in MOVES:
            rr, cc = r + 2 * dr, c + 2 * dc
            if 0 < rr < n - 1 and 0 < cc < n - 1 and g[rr][cc] == 1:
                opciones.append((dr, dc, rr, cc))
        if opciones:
            dr, dc, rr, cc = rng.choice(opciones)
            g[r + dr][c + dc] = 0
            g[rr][cc] = 0
            pila.append((rr, cc))
        else:
            pila.pop()
    if lazos > 0:
        paredes = [(r, c) for r in range(1, n - 1) for c in range(1, n - 1)
                   if g[r][c] == 1 and ((r % 2 == 1) != (c % 2 == 1))]
        rng.shuffle(paredes)
        for r, c in paredes[: int(len(paredes) * lazos)]:
            g[r][c] = 0
    return g


def laberinto_a_grafo(g):
    """Convierte la cuadricula en un grafo de networkx."""
    n = len(g)
    G = nx.Graph()
    for r in range(n):
        for c in range(n):
            if g[r][c] == 0:
                G.add_node((r, c))
                for dr, dc in ((1, 0), (0, 1)):
                    rr, cc = r + dr, c + dc
                    if rr < n and cc < n and g[rr][cc] == 0:
                        G.add_edge((r, c), (rr, cc), weight=1)
    return G


def adyacencia(G):
    """Lista de adyacencia con orden de vecinos fijo (para reproducibilidad)."""
    ady = {}
    for (r, c) in G.nodes:
        ady[(r, c)] = [(r + dr, c + dc) for dr, dc in MOVES if G.has_edge((r, c), (r + dr, c + dc))]
    return ady


# ----------------------------------------------------------------------------
# 2. Algoritmos de busqueda ciega
# ----------------------------------------------------------------------------
def reconstruir(padre, meta):
    camino = []
    nodo = meta
    while nodo is not None:
        camino.append(nodo)
        nodo = padre[nodo]
    return camino[::-1]


def bfs(ady, inicio, meta):
    """Busqueda en anchura. Frontera = cola FIFO. Devuelve (camino, expandidos,
    frontera_maxima, orden_de_expansion)."""
    frontera = deque([inicio])
    padre = {inicio: None}          # tambien funciona como conjunto de visitados
    expandidos, max_frontera, orden = 0, 1, []
    while frontera:
        nodo = frontera.popleft()
        expandidos += 1
        orden.append(nodo)
        if nodo == meta:
            return reconstruir(padre, meta), expandidos, max_frontera, orden
        for v in ady[nodo]:
            if v not in padre:
                padre[v] = nodo
                frontera.append(v)
        max_frontera = max(max_frontera, len(frontera))
    return None, expandidos, max_frontera, orden


def dfs(ady, inicio, meta):
    """Busqueda en profundidad. Frontera = pila LIFO. Se marca como visitado al
    expandir y los vecinos se apilan al reves para respetar el orden de MOVES."""
    frontera = [(inicio, None)]
    padre, visitados = {}, set()
    expandidos, max_frontera, orden = 0, 1, []
    while frontera:
        nodo, prev = frontera.pop()
        if nodo in visitados:
            continue
        visitados.add(nodo)
        padre[nodo] = prev
        expandidos += 1
        orden.append(nodo)
        if nodo == meta:
            return reconstruir(padre, meta), expandidos, max_frontera, orden
        for v in reversed(ady[nodo]):
            if v not in visitados:
                frontera.append((v, nodo))
        max_frontera = max(max_frontera, len(frontera))
    return None, expandidos, max_frontera, orden


def medir_tiempo(f, ady, ini, meta, repeticiones=15):
    tiempos = []
    for _ in range(repeticiones):
        t0 = time.perf_counter()
        f(ady, ini, meta)
        tiempos.append((time.perf_counter() - t0) * 1000)  # ms
    return statistics.median(tiempos)


# ----------------------------------------------------------------------------
# 3. Experimentos
# ----------------------------------------------------------------------------
def ejecutar(g):
    G = laberinto_a_grafo(g)
    n = len(g)
    ini, meta = (1, 1), (n - 2, n - 2)
    ady = adyacencia(G)
    fila = {"nodos_grafo": G.number_of_nodes(), "aristas_grafo": G.number_of_edges()}
    optimo = nx.shortest_path_length(G, ini, meta)
    for nombre, f in (("BFS", bfs), ("DFS", dfs)):
        camino, exp, fr, _ = f(ady, ini, meta)
        assert camino is not None and camino[0] == ini and camino[-1] == meta
        for a, b in zip(camino, camino[1:]):          # el camino es valido
            assert G.has_edge(a, b)
        fila[nombre] = {
            "pasos": len(camino) - 1,
            "expandidos": exp,
            "frontera_max": fr,
            "tiempo_ms": medir_tiempo(f, ady, ini, meta),
        }
    assert fila["BFS"]["pasos"] == optimo, "BFS debe ser optimo"
    fila["optimo_networkx"] = optimo
    return fila, G, ady, ini, meta


def dibujar_laberinto(g, caminos, titulo, archivo, orden=None):
    n = len(g)
    fig, ax = plt.subplots(figsize=(4.2, 4.2))
    ax.imshow(g, cmap=ListedColormap(["#ffffff", "#2b2b2b"]), interpolation="nearest")
    if orden:
        ys, xs = zip(*orden)
        ax.scatter(xs, ys, s=max(2, 3000 / n ** 1.4), c="#f6c177", alpha=0.7, marker="s")
    for camino, color in caminos:
        ys, xs = zip(*camino)
        ax.plot(xs, ys, color=color, lw=2)
    ax.scatter([1], [1], c="#2e9e4f", s=60, zorder=5)
    ax.scatter([n - 2], [n - 2], c="#d62728", s=60, zorder=5)
    ax.set_title(titulo, fontsize=9)
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, archivo), dpi=200)
    plt.close(fig)


def dibujar_grafo(G, camino_bfs, camino_dfs, archivo):
    pos = {(r, c): (c, -r) for (r, c) in G.nodes}
    fig, ax = plt.subplots(figsize=(5.2, 5.2))
    nx.draw_networkx_edges(G, pos, ax=ax, edge_color="#bbbbbb", width=1)
    nx.draw_networkx_nodes(G, pos, ax=ax, node_size=70, node_color="#dbe9f6",
                           edgecolors="#6b8fb3", linewidths=0.6)
    aristas_dfs = list(zip(camino_dfs, camino_dfs[1:]))
    aristas_bfs = list(zip(camino_bfs, camino_bfs[1:]))
    nx.draw_networkx_edges(G, pos, ax=ax, edgelist=aristas_dfs, edge_color="#e45756",
                           width=4, alpha=0.55)
    nx.draw_networkx_edges(G, pos, ax=ax, edgelist=aristas_bfs, edge_color="#1f6fb2", width=2.2)
    ini, meta = camino_bfs[0], camino_bfs[-1]
    nx.draw_networkx_nodes(G, pos, nodelist=[ini], node_color="#2e9e4f", node_size=170, ax=ax)
    nx.draw_networkx_nodes(G, pos, nodelist=[meta], node_color="#d62728", node_size=170, ax=ax)
    ax.set_title("Grafo del laberinto 9x9 con lazos: camino BFS (azul) y DFS (rojo)", fontsize=9)
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, archivo), dpi=200)
    plt.close(fig)


def main():
    os.makedirs(OUT, exist_ok=True)
    tamanos = [11, 21, 31, 41, 61]
    tipos = {"perfecto": 0.0, "con_lazos": 0.10}
    SEED = 42
    N_SEMILLAS = 30

    # --- 3.1 Tabla principal (semilla 42) ---------------------------------
    filas = []
    for tipo, lazos in tipos.items():
        for n in tamanos:
            f, *_ = ejecutar(generar_laberinto(n, SEED, lazos))
            filas.append({
                "laberinto": tipo, "tamano": f"{n}x{n}",
                "nodos": f["nodos_grafo"], "aristas": f["aristas_grafo"],
                "BFS_pasos": f["BFS"]["pasos"], "DFS_pasos": f["DFS"]["pasos"],
                "BFS_expandidos": f["BFS"]["expandidos"], "DFS_expandidos": f["DFS"]["expandidos"],
                "BFS_frontera": f["BFS"]["frontera_max"], "DFS_frontera": f["DFS"]["frontera_max"],
                "BFS_ms": round(f["BFS"]["tiempo_ms"], 3), "DFS_ms": round(f["DFS"]["tiempo_ms"], 3),
            })
    with open(os.path.join(OUT, "resultados_semilla42.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(filas[0].keys()))
        w.writeheader()
        w.writerows(filas)

    # --- 3.2 Promedios sobre 30 semillas ----------------------------------
    prom = []
    for tipo, lazos in tipos.items():
        for n in tamanos:
            acum = {k: [] for k in ("BFS_pasos", "DFS_pasos", "BFS_exp", "DFS_exp", "BFS_ms", "DFS_ms")}
            for s in range(N_SEMILLAS):
                f, *_ = ejecutar(generar_laberinto(n, 1000 + s, lazos))
                acum["BFS_pasos"].append(f["BFS"]["pasos"]); acum["DFS_pasos"].append(f["DFS"]["pasos"])
                acum["BFS_exp"].append(f["BFS"]["expandidos"])
                acum["DFS_exp"].append(f["DFS"]["expandidos"])
                acum["BFS_ms"].append(f["BFS"]["tiempo_ms"])
                acum["DFS_ms"].append(f["DFS"]["tiempo_ms"])
            medias = {k: round(statistics.mean(v), 3) for k, v in acum.items()}
            prom.append({"laberinto": tipo, "tamano": f"{n}x{n}", **medias})
    with open(os.path.join(OUT, "promedios_30_semillas.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(prom[0].keys()))
        w.writeheader()
        w.writerows(prom)

    # --- 3.3 Figuras -------------------------------------------------------
    # (a) laberinto 21x21 con lazos: camino BFS vs DFS y zona explorada
    g = generar_laberinto(21, SEED, 0.10)
    f, G, ady, ini, meta = ejecutar(g)
    cb, _, _, ob = bfs(ady, ini, meta)
    cd, _, _, od = dfs(ady, ini, meta)
    tit_bfs = f"BFS: {len(cb)-1} pasos, {f['BFS']['expandidos']} nodos expandidos"
    tit_dfs = f"DFS: {len(cd)-1} pasos, {f['DFS']['expandidos']} nodos expandidos"
    dibujar_laberinto(g, [(cb, "#1f6fb2")], tit_bfs, "fig_bfs.png", ob)
    dibujar_laberinto(g, [(cd, "#e45756")], tit_dfs, "fig_dfs.png", od)

    # (b) grafo pequeno 9x9 con lazos
    g9 = generar_laberinto(9, 7, 0.25)
    f9, G9, ady9, i9, m9 = ejecutar(g9)
    c9b, _, _, _ = bfs(ady9, i9, m9)
    c9d, _, _, _ = dfs(ady9, i9, m9)
    dibujar_grafo(G9, c9b, c9d, "fig_grafo9.png")
    with open(os.path.join(OUT, "demo9.txt"), "w", encoding="utf-8") as fh:
        fh.write("\n".join("".join("#" if x else "." for x in fila) for fila in g9) + "\n")
        fh.write(f"nodos={G9.number_of_nodes()} aristas={G9.number_of_edges()} "
                 f"BFS={len(c9b)-1} pasos/{f9['BFS']['expandidos']} exp, "
                 f"DFS={len(c9d)-1} pasos/{f9['DFS']['expandidos']} exp\n")

    # (c) comparacion de promedios
    import numpy as np
    fig, axs = plt.subplots(1, 3, figsize=(11, 3.4))
    x = np.arange(len(tamanos)); w = 0.38
    paneles = (("perfecto", "Nodos expandidos - laberinto perfecto"),
               ("con_lazos", "Nodos expandidos - con lazos"))
    for ax, (tipo, titulo) in zip(axs[:2], paneles):
        sub = [p for p in prom if p["laberinto"] == tipo]
        ax.bar(x - w / 2, [p["BFS_exp"] for p in sub], w, label="BFS", color="#1f6fb2")
        ax.bar(x + w / 2, [p["DFS_exp"] for p in sub], w, label="DFS", color="#e45756")
        ax.set_xticks(x); ax.set_xticklabels([p["tamano"] for p in sub], fontsize=7)
        ax.set_title(titulo, fontsize=9); ax.legend(fontsize=8)
        ax.spines[["top", "right"]].set_visible(False)
    sub = [p for p in prom if p["laberinto"] == "con_lazos"]
    tams = [p["tamano"] for p in sub]
    axs[2].plot(tams, [p["BFS_pasos"] for p in sub], "o-", color="#1f6fb2", label="BFS")
    axs[2].plot(tams, [p["DFS_pasos"] for p in sub], "o-", color="#e45756", label="DFS")
    axs[2].set_title("Longitud del camino - con lazos", fontsize=9); axs[2].legend(fontsize=8)
    axs[2].tick_params(labelsize=7); axs[2].spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "fig_comparacion.png"), dpi=200)
    plt.close(fig)

    # --- 3.4 Resumen en consola -------------------------------------------
    print("Tabla principal (semilla 42):")
    for r in filas:
        print(r)
    print("\nPromedios 30 semillas:")
    for r in prom:
        print(r)
    print(f"\nFiguras y CSV guardados en ./{OUT}")


if __name__ == "__main__":
    main()