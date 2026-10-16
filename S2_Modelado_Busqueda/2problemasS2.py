"""
Sección 2 – Modelado de problemas de búsqueda
Materia: Fundamentos de Inteligencia Artificial
Autor: Denise Estrada Franco
Fecha: 18 Octubre 2026
"""

import networkx as nx
import matplotlib.pyplot as plt
from typing import List, Tuple, Set
from matplotlib.patches import Patch

# ============================================================
# PROBLEMA 1: Red de calles (entrega urbana)
# ============================================================

def crear_grafo_calles() -> nx.DiGraph:
    """
    Genera un grafo dirigido y ponderado que representa una red de calles.
    Nodos = intersecciones. Arcos = calles de un solo sentido con coste (minutos).
    """
    G = nx.DiGraph()

    # Nodos (intersecciones)
    nodos = ["A", "B", "C", "D", "E", "F", "G"]  # A = Restaurante, G = Cliente
    G.add_nodes_from(nodos)

    # Arcos dirigidos con peso (tiempo en minutos)
    arcos = [
        ("A", "B", 4),
        ("A", "C", 2),
        ("B", "D", 5),
        ("B", "E", 3),
        ("C", "D", 1),
        ("C", "F", 6),
        ("D", "E", 2),
        ("D", "G", 4),
        ("E", "G", 3),
        ("F", "G", 2),
        ("F", "E", 1),
    ]
    G.add_weighted_edges_from(arcos)
    return G


def generador_estados_calles(G: nx.DiGraph, estado: str) -> List[Tuple[str, float]]:
    """
    Generador de estados (sucesores) para el problema de calles.
    Devuelve lista de (estado_sucesor, coste_accion).
    """
    sucesores = []
    for vecino in G.successors(estado):
        coste = G[estado][vecino]["weight"]
        sucesores.append((vecino, coste))
    return sucesores


def encontrar_ruta_optima(G: nx.DiGraph, inicio: str = "A", meta: str = "G") -> Tuple[List[str], float]:
    """Encuentra la ruta de menor coste mediante el algoritmo de Dijkstra.

    Los pesos de las aristas representan minutos estimados de viaje.
    Devuelve la lista de nodos de la ruta y el coste total.
    """
    ruta = nx.dijkstra_path(G, source=inicio, target=meta, weight="weight")
    coste_total = nx.dijkstra_path_length(G, source=inicio, target=meta, weight="weight")
    return ruta, coste_total


def dibujar_grafo_calles(
    G: nx.DiGraph,
    filename: str = "grafo_calles.png",
    ruta_optima: List[str] = None
):
    """Dibuja el grafo y resalta la ruta óptima si se proporciona."""
    pos = {
        "A": (0, 2), "B": (2, 3), "C": (2, 1),
        "D": (4, 2), "E": (5, 3), "F": (4, 0), "G": (7, 2)
    }
    plt.figure(figsize=(12, 8))

    # Colores de nodos
    node_colors = []
    for n in G.nodes():
        if n == "A":
            node_colors.append("#2ecc71")      # Verde = Inicio
        elif n == "G":
            node_colors.append("#e74c3c")      # Rojo = Meta
        else:
            node_colors.append("#3498db")      # Azul = Intermedios

    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=1400,
                           edgecolors="black", linewidths=2)

    # Etiquetas con significado
    labels = {
        "A": "A\n(Restaurante)",
        "B": "B", "C": "C", "D": "D", "E": "E", "F": "F",
        "G": "G\n(Cliente)"
    }
    nx.draw_networkx_labels(G, pos, labels, font_size=11,
                            font_weight="bold", font_color="white")

    # Resaltar las aristas que forman parte de la ruta óptima.
    aristas_ruta = set(zip(ruta_optima, ruta_optima[1:])) if ruta_optima else set()
    colores_aristas = ["#e67e22" if (u, v) in aristas_ruta else "#555555"
                       for u, v in G.edges()]
    anchos_aristas = [3.5 if (u, v) in aristas_ruta else 2.0
                      for u, v in G.edges()]
    nx.draw_networkx_edges(G, pos, edge_color=colores_aristas,
                           width=anchos_aristas, arrows=True,
                           arrowstyle="-|>", arrowsize=22,
                           connectionstyle="arc3,rad=0.05")

    edge_labels = nx.get_edge_attributes(G, "weight")
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels,
                                 font_size=11, font_color="#c0392b",
                                 bbox=dict(boxstyle="round,pad=0.2",
                                           facecolor="white", edgecolor="none", alpha=0.85))

    # Leyenda
    legend_elements = [
        Patch(facecolor="#2ecc71", edgecolor="black", label="Inicio (Restaurante)"),
        Patch(facecolor="#e74c3c", edgecolor="black", label="Meta (Cliente)"),
        Patch(facecolor="#3498db", edgecolor="black", label="Intersección intermedia")
    ]
    if ruta_optima:
        from matplotlib.lines import Line2D
        legend_elements.append(Line2D([0], [0], color="#e67e22", linewidth=3.5,
                                      label="Ruta óptima (Dijkstra)"))
    plt.legend(handles=legend_elements, loc="upper left", fontsize=10, framealpha=0.95)

    titulo = ("Problema 1 – Grafo dirigido y ponderado\n"
              "Red de calles (Entrega urbana)\n"
              "Pesos = tiempo estimado en minutos")
    if ruta_optima:
        titulo += "\nRuta óptima resaltada en naranja"
    plt.title(titulo, fontsize=14, fontweight="bold", pad=15)
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(filename, dpi=180, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Diagrama mejorado guardado: {filename}")


# ============================================================
# PROBLEMA 2: Robot de almacén (grid con obstáculos)
# ============================================================

# Mapa del almacén 4x4 (0 = libre, 1 = obstáculo)
MAPA_ALMACEN = [
    [0, 0, 0, 1],
    [0, 1, 0, 0],
    [0, 0, 0, 0],
    [1, 0, 0, 0],
]

INICIO = (0, 0)
META = (3, 2)   # ubicación del paquete


def es_valido(x: int, y: int) -> bool:
    """Verifica si la celda está dentro de límites y libre de obstáculos."""
    filas, cols = len(MAPA_ALMACEN), len(MAPA_ALMACEN[0])
    return 0 <= x < filas and 0 <= y < cols and MAPA_ALMACEN[x][y] == 0


def generador_estados_robot(estado: Tuple[int, int]) -> List[Tuple[Tuple[int, int], float]]:
    """
    Generador de estados para el robot.
    Acciones: Norte, Sur, Este, Oeste. Coste unitario = 1.
    """
    x, y = estado
    movimientos = [(-1, 0), (1, 0), (0, 1), (0, -1)]
    sucesores = []
    for dx, dy in movimientos:
        nx_, ny_ = x + dx, y + dy
        if es_valido(nx_, ny_):
            sucesores.append(((nx_, ny_), 1.0))
    return sucesores


def crear_grafo_robot() -> nx.DiGraph:
    """
    Construye el grafo dirigido completo del espacio de estados del robot
    a partir del generador de estados.
    """
    G = nx.DiGraph()
    visitados: Set[Tuple[int, int]] = set()
    cola = [INICIO]
    visitados.add(INICIO)

    while cola:
        actual = cola.pop(0)
        for sucesor, coste in generador_estados_robot(actual):
            G.add_edge(actual, sucesor, weight=coste)
            if sucesor not in visitados:
                visitados.add(sucesor)
                cola.append(sucesor)
    return G


def dibujar_grafo_robot(G: nx.DiGraph, filename: str = "grafo_robot.png"):
    """Diagrama mejorado del grafo del robot con colores, etiquetas y leyenda."""
    pos = {nodo: (nodo[1] * 1.8, -nodo[0] * 1.8) for nodo in G.nodes()}
    plt.figure(figsize=(11, 9))

    # Colores de nodos
    node_colors = []
    for n in G.nodes():
        if n == INICIO:
            node_colors.append("#2ecc71")      # Verde = Inicio
        elif n == META:
            node_colors.append("#e74c3c")      # Rojo = Meta
        else:
            node_colors.append("#9b59b6")      # Morado = Intermedios

    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=1100,
                           edgecolors="black", linewidths=2)

    labels = {n: f"({n[0]},{n[1]})" for n in G.nodes()}
    nx.draw_networkx_labels(G, pos, labels, font_size=10,
                            font_weight="bold", font_color="white")

    nx.draw_networkx_edges(G, pos, edge_color="#555555", arrows=True,
                           arrowstyle="-|>", arrowsize=18, width=1.8,
                           connectionstyle="arc3,rad=0.08")

    edge_labels = nx.get_edge_attributes(G, "weight")
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels,
                                 font_size=9, font_color="#c0392b",
                                 bbox=dict(boxstyle="round,pad=0.15",
                                           facecolor="white", edgecolor="none", alpha=0.8))

    # Leyenda
    legend_elements = [
        Patch(facecolor="#2ecc71", edgecolor="black", label=f"Inicio {INICIO} (Carga)"),
        Patch(facecolor="#e74c3c", edgecolor="black", label=f"Meta {META} (Paquete)"),
        Patch(facecolor="#9b59b6", edgecolor="black", label="Celda libre intermedia")
    ]
    plt.legend(handles=legend_elements, loc="upper right", fontsize=10, framealpha=0.95)

    plt.title("Problema 2 – Grafo dirigido del espacio de estados\n"
              "Robot de almacén (Grid 4×4 con obstáculos)\n"
              "Cada arco tiene coste = 1",
              fontsize=14, fontweight="bold", pad=15)
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(filename, dpi=180, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Diagrama mejorado guardado: {filename}")


# ============================================================
# EJECUCIÓN PRINCIPAL + ANÁLISIS DE COMPLEJIDAD
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("PROBLEMA 1 – Red de calles")
    print("=" * 60)
    G1 = crear_grafo_calles()
    print(f"Nodos: {list(G1.nodes())}")
    print(f"Arcos: {list(G1.edges(data=True))}")
    print(f"Sucesores de A: {generador_estados_calles(G1, 'A')}")

    # Buscar la ruta de menor tiempo desde el restaurante (A) hasta el cliente (G).
    ruta, coste_total = encontrar_ruta_optima(G1, inicio="A", meta="G")
    print("\nBÚSQUEDA DE RUTA ÓPTIMA CON DIJKSTRA")
    print(f"Ruta óptima: {' -> '.join(ruta)}")
    print(f"Tiempo total estimado: {coste_total} minutos")
    dibujar_grafo_calles(G1, ruta_optima=ruta)

    print("\n" + "=" * 60)
    print("PROBLEMA 2 – Robot de almacén")
    print("=" * 60)
    G2 = crear_grafo_robot()
    print(f"Número de estados alcanzables: {G2.number_of_nodes()}")
    print(f"Número de arcos: {G2.number_of_edges()}")
    print(f"Sucesores de {INICIO}: {generador_estados_robot(INICIO)}")
    dibujar_grafo_robot(G2)

    # --------------------------------------------------------
    # Análisis de complejidad
    # --------------------------------------------------------
    print("\n" + "=" * 60)
    print("ANÁLISIS DE COMPLEJIDAD")
    print("=" * 60)
    print("""
Problema 1 (grafo de calles):
  - n = número de nodos (intersecciones) = 7
  - m = número de arcos = 11
  - Generación de sucesores: O(grado del nodo) → O(1) en promedio
  - Construcción del grafo: O(n + m)
  - Espacio de estados: O(n)  (finito y pequeño)
  - Complejidad de búsqueda no informada (BFS/DFS): O(n + m)
  - Complejidad de Dijkstra / A*: O((n + m) log n) con heap

Problema 2 (grid robot):
  - Tamaño del grid: N × N = 4 × 4 → máximo 16 celdas
  - Obstáculos reducen el espacio real a aproximadamente 13 estados alcanzables
  - Factor de ramificación b ≈ 2–3 (movimientos válidos)
  - Profundidad máxima d ≤ 12
  - Generación de sucesores: O(1) (4 direcciones constantes)
  - Construcción del grafo por BFS: O(número de estados) = O(N²)
  - Espacio de estados: O(N²)
  - Búsqueda no informada: O(b^d) en el peor caso, pero en la práctica
    O(número de estados alcanzables) porque se evita revisitar estados.
  - Con A* + heurística admisible (distancia Manhattan): mucho más eficiente.
""")