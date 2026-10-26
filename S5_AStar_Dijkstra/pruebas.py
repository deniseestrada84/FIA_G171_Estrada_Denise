import math
from collections import defaultdict

from busqueda import (a_estrella, cargar_grafo, crear_heuristica, dijkstra, haversine,
                      verificar_heuristica)


def prueba_grafo_pequeno():
    """Grafo de 5 nodos con solucion conocida: A-B-D cuesta 4, A-C-D cuesta 6."""
    g = defaultdict(list)
    for u, v, c in [("A", "B", 1), ("B", "D", 3), ("A", "C", 2), ("C", "D", 4), ("D", "E", 1)]:
        g[u].append((v, c)); g[v].append((u, c))
    r = dijkstra(g, "A", "E")
    assert r.ruta == ["A", "B", "D", "E"] and r.costo == 5, r
    r2 = a_estrella(g, "A", "E", lambda n: 0)       # h = 0  ->  A* se comporta como Dijkstra
    assert r2.ruta == r.ruta and r2.costo == r.costo
    print("OK  grafo pequeno con solucion conocida")


def prueba_sin_camino():
    g = defaultdict(list)
    g["A"].append(("B", 1)); g["B"].append(("A", 1)); g["C"]  # C aislado
    assert dijkstra(g, "A", "C").ruta == [] and a_estrella(g, "A", "C", lambda n: 0).ruta == []
    print("OK  caso sin camino devuelve ruta vacia")


def prueba_inicio_igual_meta():
    coord, g = cargar_grafo()
    r = a_estrella(g, "Chalco", "Chalco", crear_heuristica(coord, "Chalco"))
    assert r.ruta == ["Chalco"] and r.costo == 0 and r.expandidos == 1
    print("OK  inicio = meta")


def prueba_astar_igual_dijkstra_en_todos_los_pares():
    coord, g = cargar_grafo()
    n = 0
    for o in coord:
        for d in coord:
            if o == d:
                continue
            rd = dijkstra(g, o, d)
            ra = a_estrella(g, o, d, crear_heuristica(coord, d))
            assert math.isclose(rd.costo, ra.costo, abs_tol=1e-9), (o, d, rd.costo, ra.costo)
            assert ra.expandidos <= rd.expandidos + 3   # A* no deberia expandir mucho mas
            n += 1
    print(f"OK  A* y Dijkstra dan el mismo costo optimo en los {n} pares")


def prueba_heuristica_admisible_y_consistente():
    coord, g = cargar_grafo()
    for meta in coord:
        no_adm, no_con, _ = verificar_heuristica(g, coord, meta)
        assert not no_adm and not no_con, (meta, no_adm, no_con)
    print(f"OK  Haversine es admisible y consistente para las {len(coord)} metas")


def prueba_heuristica_ponderada_no_admisible():
    coord, g = cargar_grafo()
    no_adm, _, _ = verificar_heuristica(g, coord, "CDMX Centro", factor=2.0)
    assert len(no_adm) > 0
    print(f"OK  2h NO es admisible ({len(no_adm)} nodos sobreestimados con meta CDMX Centro)")


def prueba_haversine():
    # 1 grado de latitud ~ 111.2 km
    assert math.isclose(haversine((19, -99), (20, -99)), 111.19, abs_tol=0.1)
    print("OK  haversine")


if __name__ == "__main__":
    prueba_grafo_pequeno()
    prueba_sin_camino()
    prueba_inicio_igual_meta()
    prueba_astar_igual_dijkstra_en_todos_los_pares()
    prueba_heuristica_admisible_y_consistente()
    prueba_heuristica_ponderada_no_admisible()
    prueba_haversine()
    print("\nTodas las pruebas pasaron.")
