
import csv
import heapq
import math
import time
from collections import defaultdict
from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# 1. Carga del grafo y heuristica
# ---------------------------------------------------------------------------
def haversine(p, q):
    """Distancia en km en linea recta entre dos puntos p=(lat, lon) y q=(lat, lon)."""
    r = 6371.0088  # radio medio de la Tierra en km
    f1, f2 = math.radians(p[0]), math.radians(q[0])
    df, dl = f2 - f1, math.radians(q[1] - p[1])
    a = math.sin(df / 2) ** 2 + math.cos(f1) * math.cos(f2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def cargar_grafo(ruta_nodos="data/nodos.csv", ruta_aristas="data/aristas.csv"):
    """Lee los CSV y devuelve (coordenadas, grafo).
    grafo[u] = lista de (vecino, costo_km). El grafo es NO dirigido (carreteras de doble sentido)."""
    coord = {}
    with open(ruta_nodos, encoding="utf-8") as f:
        for fila in csv.DictReader(f):
            coord[fila["nombre"]] = (float(fila["lat"]), float(fila["lon"]))
    grafo = defaultdict(list)
    with open(ruta_aristas, encoding="utf-8") as f:
        for fila in csv.DictReader(f):
            u, v, km = fila["origen"], fila["destino"], float(fila["km"])
            grafo[u].append((v, km))
            grafo[v].append((u, km))
    return coord, grafo


def crear_heuristica(coord, meta, factor=1.0):
    """Devuelve h(n) = factor * distancia Haversine(n, meta).
    factor = 1.0 -> admisible. factor > 1 -> A* ponderado (puede dejar de ser admisible)."""
    destino = coord[meta]
    return lambda n: factor * haversine(coord[n], destino)


# ---------------------------------------------------------------------------
# 2. Resultado de una busqueda
# ---------------------------------------------------------------------------
@dataclass
class Resultado:
    ruta: list                 # lista de nodos del inicio a la meta ([] si no hay camino)
    costo: float               # costo total g(meta) en km
    expandidos: int            # nodos sacados de la frontera y procesados
    generados: int             # nodos insertados en la frontera
    frontera_max: int          # tamano maximo de la frontera (memoria)
    tiempo_ms: float = 0.0     # tiempo de una ejecucion
    orden: list = field(default_factory=list)  # orden de expansion (para graficar)


def _reconstruir(padre, meta):
    ruta = [meta]
    while padre[ruta[-1]] is not None:
        ruta.append(padre[ruta[-1]])
    return ruta[::-1]


# ---------------------------------------------------------------------------
# 3. Dijkstra: expande siempre el nodo con menor g(n) (no usa heuristica)
# ---------------------------------------------------------------------------
def dijkstra(grafo, inicio, meta):
    t0 = time.perf_counter()
    g = {inicio: 0.0}
    padre = {inicio: None}
    frontera = [(0.0, inicio)]            # cola de prioridad ordenada por g
    expandidos, generados, fmax, orden = 0, 1, 1, []
    while frontera:
        gu, u = heapq.heappop(frontera)
        if gu > g[u]:                     # entrada vieja (ya hay un camino mejor)
            continue
        expandidos += 1
        orden.append(u)
        if u == meta:                     # al sacar la meta, el costo es optimo
            return Resultado(_reconstruir(padre, meta), gu, expandidos, generados,
                             fmax, (time.perf_counter() - t0) * 1000, orden)
        for v, costo in grafo[u]:
            nuevo = gu + costo
            if v not in g or nuevo < g[v]:    # relajacion de la arista
                g[v] = nuevo
                padre[v] = u
                heapq.heappush(frontera, (nuevo, v))
                generados += 1
        fmax = max(fmax, len(frontera))
    return Resultado([], math.inf, expandidos, generados, fmax,
                     (time.perf_counter() - t0) * 1000, orden)


# ---------------------------------------------------------------------------
# 4. A*: expande el nodo con menor f(n) = g(n) + h(n)
# ---------------------------------------------------------------------------
def a_estrella(grafo, inicio, meta, h):
    """A* con reapertura de nodos (funciona aunque h no sea consistente).
    Si h es admisible, el camino devuelto es optimo."""
    t0 = time.perf_counter()
    g = {inicio: 0.0}
    padre = {inicio: None}
    frontera = [(h(inicio), 0.0, inicio)]  # ordenada por f = g + h
    expandidos, generados, fmax, orden = 0, 1, 1, []
    while frontera:
        f, gu, u = heapq.heappop(frontera)
        if gu > g[u]:                      # entrada vieja
            continue
        expandidos += 1
        orden.append(u)
        if u == meta:
            return Resultado(_reconstruir(padre, meta), gu, expandidos, generados,
                             fmax, (time.perf_counter() - t0) * 1000, orden)
        for v, costo in grafo[u]:
            nuevo = gu + costo
            if v not in g or nuevo < g[v]:
                g[v] = nuevo
                padre[v] = u
                heapq.heappush(frontera, (nuevo + h(v), nuevo, v))
                generados += 1
        fmax = max(fmax, len(frontera))
    return Resultado([], math.inf, expandidos, generados, fmax,
                     (time.perf_counter() - t0) * 1000, orden)


# ---------------------------------------------------------------------------
# 5. Herramientas para analizar la heuristica
# ---------------------------------------------------------------------------
def costos_optimos_hacia(grafo, meta):
    """h*(n): costo real optimo de cada nodo n hacia la meta (Dijkstra completo desde la meta,
    valido porque el grafo es no dirigido)."""
    dist = {meta: 0.0}
    frontera = [(0.0, meta)]
    while frontera:
        d, u = heapq.heappop(frontera)
        if d > dist[u]:
            continue
        for v, costo in grafo[u]:
            if v not in dist or d + costo < dist[v]:
                dist[v] = d + costo
                heapq.heappush(frontera, (d + costo, v))
    return dist


def verificar_heuristica(grafo, coord, meta, factor=1.0, tol=1e-9):
    """Comprueba, para una meta dada:
       - admisibilidad: h(n) <= h*(n) para todo nodo n
       - consistencia : h(u) <= c(u,v) + h(v) para toda arista (u,v)
    Devuelve (nodos_no_admisibles, aristas_no_consistentes, razon_h/h*_maxima)."""
    h = crear_heuristica(coord, meta, factor)
    hstar = costos_optimos_hacia(grafo, meta)
    no_adm = [n for n in hstar if h(n) > hstar[n] + tol]
    no_con = [(u, v) for u in grafo for v, c in grafo[u] if h(u) > c + h(v) + tol]
    razon = max((h(n) / hstar[n] for n in hstar if hstar[n] > 0), default=0.0)
    return no_adm, no_con, razon
