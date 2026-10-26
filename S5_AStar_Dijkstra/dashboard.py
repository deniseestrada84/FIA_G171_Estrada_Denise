import csv
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")                       # sin ventana, solo guarda archivos
import matplotlib.pyplot as plt
import numpy as np

# Paleta validada (categorica, orden fijo). Cada algoritmo conserva SIEMPRE el mismo color.
C_DIJ, C_AST, C_POND = "#eb6834", "#2a78d6", "#1baf7a"
INK, INK2, GRID, SURF = "#0b0b0b", "#52514e", "#e3e2de", "#fcfcfb"

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.edgecolor": GRID,
                     "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2,
                     "text.color": INK, "figure.facecolor": SURF, "axes.facecolor": SURF})

RES = Path("results")
datos = json.loads((RES / "resultados.json").read_text(encoding="utf-8"))
pares = datos["pares"]
coord = {}
with open("data/nodos.csv", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        coord[r["nombre"]] = (float(r["lat"]), float(r["lon"]))
aristas = []
with open("data/aristas.csv", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        aristas.append((r["origen"], r["destino"]))


def estilo(ax, titulo, xlabel=None, ylabel=None):
    ax.set_title(titulo, loc="left", fontsize=10.5, fontweight="bold", color=INK, pad=8)
    ax.set_xlabel(xlabel or "")
    ax.set_ylabel(ylabel or "")
    ax.grid(axis="y", color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)


def etiqueta_par(p):
    corto = {"CDMX Centro": "CDMX", "Valle de Chalco": "V. Chalco", "Tepetlixpa": "Tepetlixpa"}
    o, d = corto.get(p["origen"], p["origen"]), corto.get(p["destino"], p["destino"])
    return f"{o}\n→ {d}"


# ---------------- Panel A: mapa del caso principal ----------------
def panel_mapa(ax):
    p = pares[0]
    orden_d, orden_a, ruta = set(p["orden_dijkstra"]), set(p["orden_astar"]), p["astar"]["ruta"]
    k = np.cos(np.radians(19.1))                       # corrige la escala longitud/latitud
    xy = {n: (lon * k, lat) for n, (lat, lon) in coord.items()}
    for a, b in aristas:
        ax.plot([xy[a][0], xy[b][0]], [xy[a][1], xy[b][1]], color=GRID, lw=1.2, zorder=1)
    ax.plot([xy[n][0] for n in ruta], [xy[n][1] for n in ruta], color=INK, lw=2.6, zorder=2,
            solid_capstyle="round")
    for n, (x, y) in xy.items():
        ax.scatter(x, y, s=14, color="#b9b8b2", zorder=3)
        if n in orden_d:
            ax.scatter(x, y, s=170, facecolors="none", edgecolors=C_DIJ, linewidths=2, zorder=4)
        if n in orden_a:
            ax.scatter(x, y, s=48, color=C_AST, zorder=5, edgecolors=SURF, linewidths=1.2)
    dx = {"Atlautla": (-0.012, -0.004), "Ozumba": (0.012, 0.012), "Tepetlixpa": (-0.012, -0.012),
          "Amecameca": (-0.012, 0.006), "Ayapango": (0.012, -0.008), "CDMX Centro": (0.016, 0.0),
          "Tlalmanalco": (0.012, 0.004), "Temamatla": (-0.012, 0.0), "Cocotitlan": (0.012, 0.006)}
    for n, (x, y) in xy.items():
        ox, oy = dx.get(n, (0.012, -0.006))
        ax.text(x + ox, y + oy, n, fontsize=6.6, color=INK2,
                ha="right" if ox < 0 else "left", va="center", zorder=6)
    estilo(ax, f"A · {p['origen']} → {p['destino']}: nodos expandidos")
    ax.grid(False)
    ax.set_xticks([]); ax.set_yticks([])
    for lado in ("left", "bottom"):
        ax.spines[lado].set_visible(False)
    ax.set_aspect("equal")
    h = [plt.Line2D([], [], marker="o", ls="", markerfacecolor="none", markeredgecolor=C_DIJ,
                    markeredgewidth=2, markersize=11, label=f"Dijkstra ({len(orden_d)} nodos)"),
         plt.Line2D([], [], marker="o", ls="", color=C_AST, markersize=7,
                    label=f"A* ({len(orden_a)} nodos)"),
         plt.Line2D([], [], color=INK, lw=2.6, label=f"Ruta óptima ({p['astar']['costo_km']:.1f} km)")]
    ax.legend(handles=h, loc="lower left", fontsize=7.5, frameon=False)


# ---------------- Paneles B y C: barras agrupadas por par ----------------
def barras(ax, clave, titulo, ylabel, fmt):
    x = np.arange(len(pares))
    ancho = 0.27
    series = [("dijkstra", "Dijkstra", C_DIJ), ("astar", "A* (h Haversine)", C_AST),
              ("astar_pond", "A* ponderado (2h)", C_POND)]
    for i, (k, nombre, color) in enumerate(series):
        vals = [p[k][clave] for p in pares]
        ax.bar(x + (i - 1) * (ancho + 0.03), vals, ancho, color=color, label=nombre, zorder=3)
    ax.set_xticks(x)
    ax.set_xticklabels([etiqueta_par(p).replace("\n", " ") for p in pares], fontsize=6.8,
                       rotation=30, ha="right", rotation_mode="anchor")
    estilo(ax, titulo, ylabel=ylabel)
    ax.legend(fontsize=7.2, frameon=False, ncol=3, loc="upper center",
              bbox_to_anchor=(0.5, 1.0), handlelength=1.2)
    ax.set_ylim(0, max(p[k][clave] for p in pares for k, _, _ in series) * 1.22)


# ---------------- Panel D: escalabilidad ----------------
def panel_escalabilidad(ax):
    esc = datos["escalabilidad"]
    n = [e["n"] for e in esc]
    d, a = [e["exp_dijkstra"] for e in esc], [e["exp_astar"] for e in esc]
    ax.plot(n, d, color=C_DIJ, lw=2, marker="o", ms=7, mec=SURF, mew=1.5)
    ax.plot(n, a, color=C_AST, lw=2, marker="o", ms=7, mec=SURF, mew=1.5)
    ax.text(n[-1], d[-1] * 1.05, "Dijkstra", color=INK, fontsize=8.5, ha="right", va="bottom")
    ax.text(n[-1], a[-1] * 1.12, "A*", color=INK, fontsize=8.5, ha="right", va="bottom")
    estilo(ax, "D · Escalabilidad (grafos aleatorios)", "Número de nodos del grafo (N)",
           "Nodos expandidos (promedio de 12 búsquedas)")


# ---------------- Panel E: admisibilidad ----------------
def panel_admisibilidad(ax):
    adm = datos["admisibilidad"]
    f = [r for r in adm["filas"] if r["hstar"] > 0]
    hs = np.array([r["hstar"] for r in f])
    lim = max(max(r["h2"] for r in f), hs.max()) * 1.05
    ax.plot([0, lim], [0, lim], color=INK2, lw=1.2, ls="--", zorder=1)
    ax.scatter(hs, [r["h2"] for r in f], s=42, color=C_POND, marker="s", edgecolors=SURF,
               linewidths=1.2, zorder=3, label="2h (no admisible)")
    ax.scatter(hs, [r["h"] for r in f], s=48, color=C_AST, edgecolors=SURF, linewidths=1.2,
               zorder=4, label="h Haversine (admisible)")
    ax.text(lim * 0.98, lim * 0.93, "h = h*", color=INK2, fontsize=8, ha="right", rotation=36)
    ax.text(lim * 0.04, lim * 0.93, "Arriba: sobreestima", color=INK2, fontsize=7.5)
    ax.text(lim * 0.96, lim * 0.03, "Abajo: admisible", color=INK2, fontsize=7.5, ha="right")
    estilo(ax, f"E · Admisibilidad (meta: {adm['meta']})", "h*(n): costo real óptimo a la meta (km)",
           "h(n): estimación (km)")
    ax.grid(axis="x", color=GRID, lw=0.8)
    ax.set_xlim(0, lim); ax.set_ylim(0, lim)
    ax.legend(fontsize=7.5, frameon=False, loc="center right", bbox_to_anchor=(1.0, 0.3))


# ---------------- Panel F: reduccion de nodos expandidos ----------------
def panel_reduccion(ax):
    x = np.arange(len(pares))
    vals = [p["reduccion_expandidos_pct"] for p in pares]
    ax.bar(x, vals, 0.6, color=C_AST, zorder=3)
    for xi, v in zip(x, vals):
        ax.text(xi, v + 1, f"{v:.0f}%", ha="center", fontsize=7.5, color=INK)
    media = datos["todos_los_pares"]["reduccion_media_pct"]
    ax.axhline(media, color=INK2, ls="--", lw=1.1, zorder=2)
    ax.text(-0.4, 64, f"Línea punteada: media en los {datos['todos_los_pares']['pares']} pares = {media:.0f}%",
            ha="left", fontsize=7.8, color=INK2)
    ax.set_xticks(x)
    ax.set_xticklabels([etiqueta_par(p).replace("\n", " ") for p in pares], fontsize=6.8,
                       rotation=30, ha="right", rotation_mode="anchor")
    ax.set_ylim(0, 70)
    estilo(ax, "F · Nodos que A* se ahorra frente a Dijkstra", ylabel="Reducción de nodos expandidos (%)")


def main():
    fig, axs = plt.subplots(2, 3, figsize=(16, 9.6), dpi=200)
    fig.suptitle("A* vs Dijkstra — rutas entre cabeceras municipales (Amecameca – Chalco – CDMX)",
                 x=0.012, ha="left", fontsize=14, fontweight="bold", color=INK)
    panel_mapa(axs[0, 0])
    barras(axs[0, 1], "expandidos", "B · Nodos expandidos por búsqueda", "Nodos expandidos", "{:d}")
    barras(axs[0, 2], "tiempo_ms", "C · Tiempo de ejecución (mediana)", "Milisegundos", "{:.3f}")
    panel_escalabilidad(axs[1, 0])
    panel_admisibilidad(axs[1, 1])
    panel_reduccion(axs[1, 2])
    fig.tight_layout(rect=(0, 0, 1, 0.95), h_pad=2.6, w_pad=2.2)
    fig.savefig(RES / "dashboard.png", facecolor=SURF)
    plt.close(fig)

    # una figura por panel (para insertarlas por separado en el PDF)
    nombres = [("fig_mapa", panel_mapa, (6.2, 5.6)),
               ("fig_nodos", lambda a: barras(a, "expandidos", "Nodos expandidos por búsqueda",
                                              "Nodos expandidos", "{:d}"), (7.4, 4.4)),
               ("fig_tiempo", lambda a: barras(a, "tiempo_ms", "Tiempo de ejecución (mediana)",
                                               "Milisegundos", "{:.3f}"), (7.4, 4.4)),
               ("fig_escalabilidad", panel_escalabilidad, (6.2, 4.4)),
               ("fig_admisibilidad", panel_admisibilidad, (6.2, 4.6)),
               ("fig_reduccion", panel_reduccion, (7.4, 4.4))]
    for nombre, fn, tam in nombres:
        fig, ax = plt.subplots(figsize=tam, dpi=200)
        fn(ax)
        fig.tight_layout()
        fig.savefig(RES / f"{nombre}.png", facecolor=SURF)
        plt.close(fig)
    print("Dashboard guardado en results/dashboard.png")


if __name__ == "__main__":
    main()
