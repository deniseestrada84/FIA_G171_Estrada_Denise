import csv
import json
import math
import random
import statistics
from collections import defaultdict
from pathlib import Path

import numpy as np

from busqueda import (a_estrella, cargar_grafo, crear_heuristica, costos_optimos_hacia,
                      dijkstra, verificar_heuristica)

SALIDA = Path("results")
SALIDA.mkdir(exist_ok=True)
REPETICIONES = 300          # ejecuciones por algoritmo para medir tiempo (se usa la mediana)
FACTOR_PONDERADO = 2.0      # A* ponderado: h' = 2 * h  (NO admisible, se usa para comparar)

# Casos de prueba (origen, destino). El primero es el caso principal del informe.
PARES = [
    ("Atlautla", "CDMX Centro"),
    ("Ecatzingo", "CDMX Centro"),
    ("Ozumba", "Xochimilco"),
    ("Amecameca", "Ixtapaluca"),
    ("Tepetlixpa", "Valle de Chalco"),
    ("Juchitepec", "Tlahuac"),
    ("Ecatzingo", "Milpa Alta"),
    ("Atlautla", "Chalco"),
]


def tiempo_mediano(funcion, repeticiones=REPETICIONES):
    """Ejecuta 'funcion' varias veces y devuelve (ultimo_resultado, mediana_ms)."""
    tiempos = []
    for _ in range(repeticiones):
        r = funcion()
        tiempos.append(r.tiempo_ms)
    return r, statistics.median(tiempos)


def resumen(r, t_ms):
    return {"costo_km": round(r.costo, 3), "expandidos": r.expandidos, "generados": r.generados,
            "frontera_max": r.frontera_max, "tiempo_ms": round(t_ms, 4), "ruta": r.ruta}


def experimento_pares(coord, grafo):
    filas = []
    for ori, dest in PARES:
        h = crear_heuristica(coord, dest)
        h2 = crear_heuristica(coord, dest, FACTOR_PONDERADO)
        rd, td = tiempo_mediano(lambda: dijkstra(grafo, ori, dest))
        ra, ta = tiempo_mediano(lambda: a_estrella(grafo, ori, dest, h))
        rp, tp = tiempo_mediano(lambda: a_estrella(grafo, ori, dest, h2))
        filas.append({
            "origen": ori, "destino": dest,
            "dijkstra": resumen(rd, td), "astar": resumen(ra, ta), "astar_pond": resumen(rp, tp),
            "optimo_igual": abs(rd.costo - ra.costo) < 1e-9,
            "reduccion_expandidos_pct": round(100 * (1 - ra.expandidos / rd.expandidos), 1),
            "sobrecosto_pond_pct": round(100 * (rp.costo / rd.costo - 1), 2),
            "orden_dijkstra": rd.orden, "orden_astar": ra.orden,
        })
    return filas


def experimento_todos_los_pares(coord, grafo):
    """Compara los dos algoritmos en los 18 x 17 = 306 pares origen-destino posibles."""
    nodos = list(coord)
    red, subopt, distintos = [], 0, 0
    sobrecostos = []
    for ori in nodos:
        for dest in nodos:
            if ori == dest:
                continue
            rd = dijkstra(grafo, ori, dest)
            ra = a_estrella(grafo, ori, dest, crear_heuristica(coord, dest))
            rp = a_estrella(grafo, ori, dest, crear_heuristica(coord, dest, FACTOR_PONDERADO))
            if abs(rd.costo - ra.costo) > 1e-9:
                distintos += 1
            if rp.costo > rd.costo + 1e-9:
                subopt += 1
                sobrecostos.append(100 * (rp.costo / rd.costo - 1))
            red.append(100 * (1 - ra.expandidos / rd.expandidos))
    return {"pares": len(red), "astar_no_optimo": distintos,
            "reduccion_media_pct": round(statistics.mean(red), 1),
            "reduccion_min_pct": round(min(red), 1), "reduccion_max_pct": round(max(red), 1),
            "pond_suboptimos": subopt,
            "pond_sobrecosto_max_pct": round(max(sobrecostos), 2) if sobrecostos else 0.0}


def experimento_admisibilidad(coord, grafo, meta="CDMX Centro"):
    h = crear_heuristica(coord, meta)
    h2 = crear_heuristica(coord, meta, FACTOR_PONDERADO)
    hstar = costos_optimos_hacia(grafo, meta)
    filas = [{"nodo": n, "h": round(h(n), 3), "hstar": round(hstar[n], 3), "h2": round(h2(n), 3)}
             for n in coord]
    # verificacion contra TODAS las metas posibles
    adm_ok = con_ok = adm2_ok = con2_ok = 0
    razones = []
    for m in coord:
        a, c, rz = verificar_heuristica(grafo, coord, m, 1.0)
        a2, c2, _ = verificar_heuristica(grafo, coord, m, FACTOR_PONDERADO)
        adm_ok += not a
        con_ok += not c
        adm2_ok += not a2
        con2_ok += not c2
        razones.append(rz)
    return {"meta": meta, "filas": filas, "metas_probadas": len(coord),
            "h_admisible_en": adm_ok, "h_consistente_en": con_ok,
            "h2_admisible_en": adm2_ok, "h2_consistente_en": con2_ok,
            "razon_h_hstar_maxima": round(max(razones), 3),
            "razon_h_hstar_media_meta": round(statistics.mean(
                f["h"] / f["hstar"] for f in filas if f["hstar"] > 0), 3)}


# ---------------------------------------------------------------------------
# Escalabilidad: grafos aleatorios geometricos de N nodos (k vecinos mas cercanos)
# ---------------------------------------------------------------------------
def grafo_aleatorio(n, semilla, k=6):
    rng = np.random.default_rng(semilla)
    pts = rng.uniform(0, 100, size=(n, 2))                     # plano de 100 x 100 km
    grafo = defaultdict(list)
    vistos = set()
    for i in range(n):
        d = np.hypot(pts[:, 0] - pts[i, 0], pts[:, 1] - pts[i, 1])
        for j in np.argsort(d)[1:k + 1]:
            j = int(j)
            if (min(i, j), max(i, j)) in vistos:
                continue
            vistos.add((min(i, j), max(i, j)))
            costo = float(d[j]) * float(rng.uniform(1.0, 1.3))  # costo >= distancia recta
            grafo[i].append((j, costo))
            grafo[j].append((i, costo))
    return pts, grafo


def experimento_escalabilidad(tamanos=(250, 500, 1000, 2000, 4000), grafos=3, pares=4):
    filas = []
    for n in tamanos:
        exp_d, exp_a, t_d, t_a = [], [], [], []
        for s in range(grafos):
            pts, grafo = grafo_aleatorio(n, semilla=1000 * n + s)
            rnd = random.Random(s + n)
            hechos = 0
            while hechos < pares:
                a, b = rnd.randrange(n), rnd.randrange(n)
                if math.dist(pts[a], pts[b]) < 70:             # origen y destino lejanos
                    continue
                h = lambda x, b=b: float(math.dist(pts[x], pts[b]))
                rd = dijkstra(grafo, a, b)
                if not rd.ruta:                                  # sin camino: otro par
                    continue
                ra = a_estrella(grafo, a, b, h)
                assert abs(rd.costo - ra.costo) < 1e-9
                exp_d.append(rd.expandidos); exp_a.append(ra.expandidos)
                t_d.append(rd.tiempo_ms); t_a.append(ra.tiempo_ms)
                hechos += 1
        filas.append({"n": n, "pares": len(exp_d),
                      "exp_dijkstra": round(statistics.mean(exp_d), 1),
                      "exp_astar": round(statistics.mean(exp_a), 1),
                      "t_dijkstra_ms": round(statistics.mean(t_d), 3),
                      "t_astar_ms": round(statistics.mean(t_a), 3),
                      "reduccion_pct": round(100 * (1 - statistics.mean(exp_a) / statistics.mean(exp_d)), 1)})
    return filas


def main():
    coord, grafo = cargar_grafo()
    print(f"Grafo: {len(coord)} nodos, {sum(len(v) for v in grafo.values()) // 2} aristas\n")

    pares = experimento_pares(coord, grafo)
    print(f"{'Origen -> Destino':38s} {'km':>7s} {'Dij exp':>8s} {'A* exp':>7s} {'red%':>6s} "
          f"{'Dij ms':>8s} {'A* ms':>7s}")
    for p in pares:
        print(f"{p['origen'] + ' -> ' + p['destino']:38s} {p['dijkstra']['costo_km']:7.2f} "
              f"{p['dijkstra']['expandidos']:8d} {p['astar']['expandidos']:7d} "
              f"{p['reduccion_expandidos_pct']:6.1f} {p['dijkstra']['tiempo_ms']:8.4f} "
              f"{p['astar']['tiempo_ms']:7.4f}")

    todos = experimento_todos_los_pares(coord, grafo)
    adm = experimento_admisibilidad(coord, grafo)
    esc = experimento_escalabilidad()
    print("\nTodos los pares:", todos)
    print("Admisibilidad:", {k: v for k, v in adm.items() if k != "filas"})
    print("Escalabilidad:")
    for e in esc:
        print("  ", e)

    # El caso principal guarda el orden de expansion para dibujarlo en el dashboard
    resultados = {"grafo": {"nodos": len(coord), "aristas": sum(len(v) for v in grafo.values()) // 2},
                  "factor_ponderado": FACTOR_PONDERADO, "repeticiones": REPETICIONES,
                  "pares": pares, "todos_los_pares": todos, "admisibilidad": adm,
                  "escalabilidad": esc}
    (SALIDA / "resultados.json").write_text(json.dumps(resultados, indent=2, ensure_ascii=False),
                                            encoding="utf-8")
    with open(SALIDA / "comparativa_pares.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["origen", "destino", "costo_km", "dijkstra_expandidos", "astar_expandidos",
                    "reduccion_pct", "dijkstra_ms", "astar_ms", "astar_pond_costo_km"])
        for p in pares:
            w.writerow([p["origen"], p["destino"], p["dijkstra"]["costo_km"],
                        p["dijkstra"]["expandidos"], p["astar"]["expandidos"],
                        p["reduccion_expandidos_pct"], p["dijkstra"]["tiempo_ms"],
                        p["astar"]["tiempo_ms"], p["astar_pond"]["costo_km"]])
    with open(SALIDA / "escalabilidad.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(esc[0]))
        w.writeheader()
        w.writerows(esc)
    print("\nResultados guardados en results/")


if __name__ == "__main__":
    main()
