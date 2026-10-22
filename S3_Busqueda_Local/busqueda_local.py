"""
Actividad Parcial 2 - Fundamentos de Inteligencia Artificial
Seccion 3 (2.3 Busqueda Local): Hill Climbing y Simulated Annealing

Problema: Ruta minima (TSP) que visita 18 capitales de estado de Mexico una sola vez
y regresa al origen. La funcion objetivo es la distancia total (km) del ciclo.

Ejecucion:  python busqueda_local.py
Genera:     resultados.json y las graficas .png en la carpeta ./figuras
"""
import json
import math
import os
import random
import time

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter

# ----------------------------------------------------------------------------
# 1. DATOS DEL PROBLEMA (coordenadas aproximadas: latitud, longitud en grados)
# ----------------------------------------------------------------------------
CIUDADES = {
    "Ciudad de Mexico": (19.43, -99.13),
    "Toluca": (19.29, -99.65),
    "Cuernavaca": (18.92, -99.23),
    "Puebla": (19.04, -98.20),
    "Tlaxcala": (19.32, -98.24),
    "Pachuca": (20.12, -98.73),
    "Queretaro": (20.59, -100.39),
    "Morelia": (19.70, -101.19),
    "Guanajuato": (21.02, -101.26),
    "San Luis Potosi": (22.15, -100.98),
    "Aguascalientes": (21.88, -102.29),
    "Guadalajara": (20.67, -103.35),
    "Zacatecas": (22.77, -102.58),
    "Monterrey": (25.67, -100.31),
    "Xalapa": (19.54, -96.91),
    "Oaxaca": (17.07, -96.72),
    "Chilpancingo": (17.55, -99.50),
    "Villahermosa": (17.99, -92.93),
}
NOMBRES = list(CIUDADES.keys())
N = len(NOMBRES)


def haversine(a, b):
    """Distancia en km entre dos puntos (lat, lon) sobre la esfera terrestre."""
    r = 6371.0
    la1, lo1, la2, lo2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    d = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 2 * r * math.asin(math.sqrt(d))


# Matriz de distancias precalculada (N x N)
D = np.array([[haversine(CIUDADES[i], CIUDADES[j]) for j in NOMBRES] for i in NOMBRES])


# ----------------------------------------------------------------------------
# 2. FUNCION OBJETIVO Y VECINDARIO
# ----------------------------------------------------------------------------
def costo(ruta):
    """Funcion objetivo f(ruta): longitud total del ciclo en km (se MINIMIZA)."""
    return sum(D[ruta[i], ruta[(i + 1) % N]] for i in range(N))


def delta_2opt(ruta, i, j):
    """Cambio de costo al invertir el segmento ruta[i..j] (vecino 2-opt), en O(1)."""
    a, b = ruta[i - 1], ruta[i]
    c, d = ruta[j], ruta[(j + 1) % N]
    return D[a, c] + D[b, d] - D[a, b] - D[c, d]


def vecino_aleatorio(ruta, rng):
    """Genera un vecino 2-opt: elige i<j al azar. Devuelve (i, j, delta)."""
    i, j = sorted(rng.sample(range(1, N), 2))
    return i, j, delta_2opt(ruta, i, j)


def aplicar_2opt(ruta, i, j):
    return ruta[:i] + ruta[i:j + 1][::-1] + ruta[j + 1:]


def ruta_inicial(rng):
    r = list(range(N))
    rng.shuffle(r)
    return r


# ----------------------------------------------------------------------------
# 3. ALGORITMOS
# ----------------------------------------------------------------------------
def hill_climbing(semilla, iteraciones=20000):
    """
    Hill Climbing estocastico (primera mejora): en cada iteracion se genera UN
    vecino 2-opt al azar y se acepta solo si reduce el costo (delta < 0).
    Se queda atrapado en minimos locales: no acepta jamas un empeoramiento.
    """
    rng = random.Random(semilla)
    ruta = ruta_inicial(rng)
    actual = costo(ruta)
    historial = [actual]
    for _ in range(iteraciones):
        i, j, delta = vecino_aleatorio(ruta, rng)
        if delta < -1e-9:
            ruta = aplicar_2opt(ruta, i, j)
            actual += delta
        historial.append(actual)
    return ruta, actual, historial


def simulated_annealing(semilla, iteraciones=20000, T0=300.0, eta=0.9995):
    """
    Recocido Simulado. Parametros:
      T0  : temperatura inicial (en km, misma unidad que el costo)
      eta : factor de enfriamiento geometrico, T <- eta * T en cada iteracion
    Si delta < 0 se acepta siempre; si delta >= 0 se acepta con prob. exp(-delta/T),
    lo que permite escapar de minimos locales al inicio (T alta).
    Se conserva la mejor ruta encontrada.
    """
    rng = random.Random(semilla)
    ruta = ruta_inicial(rng)
    actual = costo(ruta)
    mejor_ruta, mejor = ruta[:], actual
    T = T0
    hist_actual, hist_mejor = [actual], [mejor]
    for _ in range(iteraciones):
        i, j, delta = vecino_aleatorio(ruta, rng)
        if delta < 0 or rng.random() < math.exp(-delta / T):
            ruta = aplicar_2opt(ruta, i, j)
            actual += delta
            if actual < mejor - 1e-9:
                mejor, mejor_ruta = actual, ruta[:]
        T *= eta
        hist_actual.append(actual)
        hist_mejor.append(mejor)
    return mejor_ruta, mejor, hist_mejor, hist_actual


def optimo_exacto():
    """Held-Karp (programacion dinamica) para obtener el optimo REAL de referencia."""
    inf = float("inf")
    n = N
    dp = np.full((1 << (n - 1), n - 1), inf)  # ciudad 0 es el origen; subconjuntos de 1..n-1
    padre = np.full((1 << (n - 1), n - 1), -1, dtype=np.int32)
    for k in range(n - 1):
        dp[1 << k, k] = D[0, k + 1]
    for mask in range(1, 1 << (n - 1)):
        for k in range(n - 1):
            if not (mask >> k) & 1 or dp[mask, k] == inf:
                continue
            for m in range(n - 1):
                if (mask >> m) & 1:
                    continue
                nm = mask | (1 << m)
                c = dp[mask, k] + D[k + 1, m + 1]
                if c < dp[nm, m]:
                    dp[nm, m] = c
                    padre[nm, m] = k
    full = (1 << (n - 1)) - 1
    fin = min(range(n - 1), key=lambda k: dp[full, k] + D[k + 1, 0])
    mejor = dp[full, fin] + D[fin + 1, 0]
    ruta, mask, k = [], full, fin
    while k != -1:
        ruta.append(k + 1)
        pk = padre[mask, k]
        mask ^= 1 << k
        k = pk
    ruta.append(0)
    return ruta[::-1], float(mejor)


# ----------------------------------------------------------------------------
# 4. EXPERIMENTOS
# ----------------------------------------------------------------------------
def ejecutar_hc_con_rastros(semilla, iteraciones=20000, paso=200):
    """Ejecuta Hill Climbing y guarda muestras de la ruta para animarla."""
    rng = random.Random(semilla)
    ruta = ruta_inicial(rng)
    actual = costo(ruta)
    historial = [actual]
    rutas_muestra = [ruta[:]]
    pasos = [0]
    for k in range(1, iteraciones + 1):
        i, j, delta = vecino_aleatorio(ruta, rng)
        if delta < -1e-9:
            ruta = aplicar_2opt(ruta, i, j)
            actual += delta
        historial.append(actual)
        if k % paso == 0 or k == iteraciones:
            rutas_muestra.append(ruta[:])
            pasos.append(k)
    return rutas_muestra, pasos, historial


def ejecutar_sa_con_rastros(semilla, iteraciones=20000, T0=300.0, eta=0.9995, paso=200):
    """Ejecuta Simulated Annealing y guarda rutas actuales y mejor ruta para animarlas."""
    rng = random.Random(semilla)
    ruta = ruta_inicial(rng)
    actual = costo(ruta)
    mejor_ruta, mejor = ruta[:], actual
    T = T0
    historial_actual = [actual]
    historial_mejor = [mejor]
    rutas_muestra = [ruta[:]]
    mejores_muestra = [mejor_ruta[:]]
    pasos = [0]
    for k in range(1, iteraciones + 1):
        i, j, delta = vecino_aleatorio(ruta, rng)
        if delta < 0 or rng.random() < math.exp(-delta / max(T, 1e-12)):
            ruta = aplicar_2opt(ruta, i, j)
            actual += delta
            if actual < mejor - 1e-9:
                mejor, mejor_ruta = actual, ruta[:]
        T *= eta
        historial_actual.append(actual)
        historial_mejor.append(mejor)
        if k % paso == 0 or k == iteraciones:
            rutas_muestra.append(ruta[:])
            mejores_muestra.append(mejor_ruta[:])
            pasos.append(k)
    return rutas_muestra, mejores_muestra, pasos, historial_actual, historial_mejor


def guardar_animacion(nombre_archivo, titulo, rutas, pasos, historial, ruta_mejor=None,
                      historial_mejor=None, fps=8):
    """Guarda un GIF con la ruta cambiando en el mapa y la convergencia en tiempo real."""
    fig, (ax_mapa, ax_costo) = plt.subplots(1, 2, figsize=(10, 4), dpi=70)
    coords = np.array([CIUDADES[n] for n in NOMBRES])
    latitudes, longitudes = coords[:, 0], coords[:, 1]
    ax_mapa.scatter(longitudes, latitudes, s=24, color="#333333", zorder=3)
    for idx, nombre in enumerate(NOMBRES):
        etiqueta = nombre.replace("Ciudad de Mexico", "CDMX")
        ax_mapa.annotate(etiqueta, (longitudes[idx], latitudes[idx]), fontsize=6,
                         xytext=(3, 3), textcoords="offset points")
    ax_mapa.set_xlabel("Longitud")
    ax_mapa.set_ylabel("Latitud")
    ax_mapa.set_title("Ruta actual")
    ax_mapa.grid(alpha=0.2)
    linea_ruta, = ax_mapa.plot([], [], "-o", lw=1.8, ms=3.5, color="#1b5e9b", zorder=2)
    linea_mejor = None
    if ruta_mejor is not None:
        linea_mejor, = ax_mapa.plot([], [], "--", lw=1.5, color="#2e7d32", alpha=0.9,
                                    label="Mejor ruta encontrada")
        ax_mapa.legend(loc="lower left", fontsize=8)

    x = np.arange(len(historial))
    linea_costo, = ax_costo.plot([], [], color="#d95f02", lw=1.5, label="Costo actual")
    linea_mejor_costo = None
    if historial_mejor is not None:
        linea_mejor_costo, = ax_costo.plot([], [], color="#2e7d32", lw=1.8, label="Mejor costo")
        ax_costo.legend(frameon=False, fontsize=8)
    ax_costo.set_xlim(0, len(historial) - 1)
    minimo = min(min(historial), min(historial_mejor) if historial_mejor is not None else min(historial))
    maximo = max(historial)
    if historial_mejor is not None:
        maximo = max(maximo, max(historial_mejor))
    margen = max((maximo - minimo) * 0.08, 20)
    ax_costo.set_ylim(minimo - margen, maximo + margen)
    ax_costo.set_xlabel("Iteración")
    ax_costo.set_ylabel("Distancia total (km)")
    ax_costo.set_title("Evolución del costo")
    ax_costo.grid(alpha=0.2)
    texto = fig.suptitle(titulo, fontsize=12, fontweight="bold")

    def actualizar(frame):
        ruta = rutas[frame]
        ruta_cerrada = ruta + [ruta[0]]
        xs = [CIUDADES[NOMBRES[i]][1] for i in ruta_cerrada]
        ys = [CIUDADES[NOMBRES[i]][0] for i in ruta_cerrada]
        linea_ruta.set_data(xs, ys)
        paso_actual = pasos[frame]
        linea_costo.set_data(x[:paso_actual + 1], historial[:paso_actual + 1])
        if linea_mejor_costo is not None:
            linea_mejor_costo.set_data(x[:paso_actual + 1], historial_mejor[:paso_actual + 1])
        costo_actual = historial[paso_actual]
        texto.set_text(f"{titulo} | Iteración {paso_actual:,} | Costo actual: {costo_actual:,.1f} km")
        if linea_mejor is not None:
            r_mejor = ruta_mejor[frame] + [ruta_mejor[frame][0]]
            linea_mejor.set_data([CIUDADES[NOMBRES[i]][1] for i in r_mejor],
                                 [CIUDADES[NOMBRES[i]][0] for i in r_mejor])
        return (linea_ruta, linea_costo, texto) if linea_mejor is None else (linea_ruta, linea_mejor, linea_costo, linea_mejor_costo, texto)

    anim = FuncAnimation(fig, actualizar, frames=len(rutas), interval=1000 // fps, blit=False)
    anim.save(nombre_archivo, writer=PillowWriter(fps=fps), dpi=70)
    plt.close(fig)


def generar_animaciones():
    """Genera GIFs animados para observar el cambio de ruta y la convergencia."""
    os.makedirs("figuras", exist_ok=True)
    iteraciones_anim = 20000
    paso_anim = 500  # una imagen cada 500 iteraciones: 41 cuadros por GIF

    rutas_hc, pasos_hc, hist_hc = ejecutar_hc_con_rastros(semilla=42,
                                                           iteraciones=iteraciones_anim,
                                                           paso=paso_anim)
    guardar_animacion("figuras/animacion_hill_climbing.gif",
                      "Hill Climbing: búsqueda local", rutas_hc, pasos_hc, hist_hc)

    rutas_sa, mejores_sa, pasos_sa, hist_actual_sa, hist_mejor_sa = ejecutar_sa_con_rastros(
        semilla=42, iteraciones=iteraciones_anim, T0=300.0, eta=0.9995, paso=paso_anim)
    guardar_animacion("figuras/animacion_simulated_annealing.gif",
                      "Simulated Annealing: ruta actual y mejor ruta", rutas_sa, pasos_sa,
                      hist_actual_sa, ruta_mejor=mejores_sa,
                      historial_mejor=hist_mejor_sa)
    print("Animaciones guardadas en:")
    print(" - figuras/animacion_hill_climbing.gif")
    print(" - figuras/animacion_simulated_annealing.gif")


def main():
    os.makedirs("figuras", exist_ok=True)
    ITER, CORRIDAS = 20000, 30
    T0, ETA = 300.0, 0.9995
    semillas = list(range(1, CORRIDAS + 1))

    # 4.1 Corridas principales (mismas semillas => mismo punto de partida para ambos)
    t = time.time()
    hc = [hill_climbing(s, ITER) for s in semillas]
    t_hc = time.time() - t
    t = time.time()
    sa = [simulated_annealing(s, ITER, T0, ETA) for s in semillas]
    t_sa = time.time() - t
    costos_hc = np.array([r[1] for r in hc])
    costos_sa = np.array([r[1] for r in sa])
    inicio = np.array([r[2][0] for r in sa])  # costo inicial (iteracion 0)

    # 4.2 Optimo exacto de referencia
    t = time.time()
    ruta_opt, costo_opt = optimo_exacto()
    t_opt = time.time() - t

    # 4.3 Sensibilidad de parametros de SA (10 corridas por combinacion)
    sens = []
    for T0s in (10, 100, 300, 1000):
        for etas in (0.999, 0.9995, 0.9999):
            cs = [simulated_annealing(s, ITER, T0s, etas)[1] for s in range(1, 11)]
            sens.append({"T0": T0s, "eta": etas, "media": float(np.mean(cs)),
                         "mejor": float(np.min(cs)), "peor": float(np.max(cs))})

    # 4.4 Efecto del numero de iteraciones (10 corridas)
    iters_tab = []
    for it in (1000, 5000, 20000, 50000):
        eta_it = 0.9995 ** (20000 / it)  # mismo enfriamiento total para todas
        h = [hill_climbing(s, it)[1] for s in range(1, 11)]
        a = [simulated_annealing(s, it, T0, eta_it)[1] for s in range(1, 11)]
        iters_tab.append({"iter": it, "hc_media": float(np.mean(h)), "sa_media": float(np.mean(a))})

    ib_hc, ib_sa = int(np.argmin(costos_hc)), int(np.argmin(costos_sa))
    resumen = {
        "n_ciudades": N, "iteraciones": ITER, "corridas": CORRIDAS, "T0": T0, "eta": ETA,
        "costo_inicial_medio": float(np.mean(inicio)),
        "optimo_exacto_km": costo_opt, "ruta_optima": [NOMBRES[i] for i in ruta_opt],
        "tiempo_optimo_s": t_opt,
        "hc": {"media": float(costos_hc.mean()), "desv": float(costos_hc.std(ddof=1)),
               "mejor": float(costos_hc.min()), "peor": float(costos_hc.max()),
               "mediana": float(np.median(costos_hc)), "tiempo_s": t_hc,
               "aciertos_optimo": int(np.sum(costos_hc <= costo_opt + 0.5)),
               "ruta": [NOMBRES[i] for i in hc[ib_hc][0]]},
        "sa": {"media": float(costos_sa.mean()), "desv": float(costos_sa.std(ddof=1)),
               "mejor": float(costos_sa.min()), "peor": float(costos_sa.max()),
               "mediana": float(np.median(costos_sa)), "tiempo_s": t_sa,
               "aciertos_optimo": int(np.sum(costos_sa <= costo_opt + 0.5)),
               "ruta": [NOMBRES[i] for i in sa[ib_sa][0]]},
        "sensibilidad": sens, "iteraciones_tab": iters_tab,
        "costos_hc": costos_hc.tolist(), "costos_sa": costos_sa.tolist(),
    }
    with open("resultados.json", "w", encoding="utf-8") as f:
        json.dump(resumen, f, ensure_ascii=False, indent=2)

    # ------------------------------------------------------------------------
    # 5. GRAFICAS
    # ------------------------------------------------------------------------
    c_hc, c_sa, c_opt = "#d95f02", "#1b5e9b", "#2e7d32"
    plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False})

    # 5.1 Convergencia (media y banda min-max sobre las 30 corridas + una corrida)
    H = np.array([r[2] for r in hc])
    S = np.array([r[2] for r in sa])
    x = np.arange(ITER + 1)
    fig, ax = plt.subplots(1, 2, figsize=(11, 4.2))
    for a, escala in zip(ax, ("lineal", "log")):
        a.fill_between(x, H.min(0), H.max(0), color=c_hc, alpha=0.15)
        a.fill_between(x, S.min(0), S.max(0), color=c_sa, alpha=0.15)
        a.plot(x, H.mean(0), color=c_hc, lw=2, label="Hill Climbing (media)")
        a.plot(x, S.mean(0), color=c_sa, lw=2, label="Simulated Annealing (media)")
        a.axhline(costo_opt, color=c_opt, ls="--", lw=1.5, label=f"Optimo exacto ({costo_opt:,.0f} km)")
        a.set_xlabel("Iteracion")
        a.set_ylabel("Mejor costo (km)")
        if escala == "log":
            a.set_xscale("log")
            a.set_title("Escala logaritmica en X")
        else:
            a.set_title("Convergencia (banda = min-max de 30 corridas)")
            a.legend(frameon=False, fontsize=8)
        a.set_ylim(costo_opt * 0.95, H.mean(0)[0] * 1.02)
    fig.tight_layout()
    fig.savefig("figuras/convergencia.png", dpi=170)
    plt.close(fig)

    # 5.2 Temperatura y costo actual de SA (muestra aceptacion de empeoramientos)
    fig, ax = plt.subplots(figsize=(6.2, 3.8))
    s0 = sa[ib_sa][3]
    ax.plot(s0, color=c_sa, lw=0.8, label="Costo actual (SA)")
    ax.plot(sa[ib_sa][2], color="k", lw=1.5, label="Mejor hasta el momento")
    ax.set_xlabel("Iteracion")
    ax.set_ylabel("Costo (km)")
    ax.set_title("SA: la ruta actual sube y baja mientras T es alta")
    ax.set_ylim(costo_opt * 0.95, max(s0[:3000]) * 1.02)
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig("figuras/sa_actual_vs_mejor.png", dpi=170)
    plt.close(fig)

    # 5.3 Rutas finales sobre el mapa (lon, lat)
    def dibujar(a, ruta_idx, titulo, color):
        pts = [CIUDADES[NOMBRES[i]] for i in ruta_idx] + [CIUDADES[NOMBRES[ruta_idx[0]]]]
        a.plot([p[1] for p in pts], [p[0] for p in pts], "-o", color=color, lw=1.6, ms=4)
        for i in ruta_idx:
            la, lo = CIUDADES[NOMBRES[i]]
            a.annotate(NOMBRES[i].replace("Ciudad de Mexico", "CDMX"), (lo, la), fontsize=6.5,
                       xytext=(3, 3), textcoords="offset points")
        a.set_title(titulo, fontsize=9)
        a.set_xlabel("Longitud")
        a.set_ylabel("Latitud")
    fig, ax = plt.subplots(1, 3, figsize=(12.5, 4.4))
    dibujar(ax[0], hc[ib_hc][0], f"Hill Climbing (mejor): {costos_hc.min():,.0f} km", c_hc)
    dibujar(ax[1], sa[ib_sa][0], f"Simulated Annealing (mejor): {costos_sa.min():,.0f} km", c_sa)
    dibujar(ax[2], ruta_opt, f"Optimo exacto (Held-Karp): {costo_opt:,.0f} km", c_opt)
    fig.tight_layout()
    fig.savefig("figuras/rutas.png", dpi=170)
    plt.close(fig)

    # 5.4 Comparacion de resultados finales (30 corridas)
    fig, ax = plt.subplots(figsize=(6.2, 4))
    bp = ax.boxplot([costos_hc, costos_sa], tick_labels=["Hill Climbing", "Simulated Annealing"],
                    patch_artist=True, widths=0.5)
    for patch, col in zip(bp["boxes"], (c_hc, c_sa)):
        patch.set_facecolor(col)
        patch.set_alpha(0.45)
    for k, vals in enumerate((costos_hc, costos_sa), start=1):
        ax.scatter(np.random.default_rng(0).normal(k, 0.04, len(vals)), vals, s=14, color="k", alpha=0.6, zorder=3)
    ax.axhline(costo_opt, color=c_opt, ls="--", label=f"Optimo exacto ({costo_opt:,.0f} km)")
    ax.set_ylabel("Costo final (km)")
    ax.set_title("Resultado final en 30 corridas")
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig("figuras/comparacion.png", dpi=170)
    plt.close(fig)

    # 5.5 Sensibilidad de parametros (mapa de calor, costo medio de SA)
    T0s = sorted({s["T0"] for s in sens})
    etas = sorted({s["eta"] for s in sens})
    M = np.array([[next(s["media"] for s in sens if s["T0"] == t0 and s["eta"] == e) for e in etas] for t0 in T0s])
    fig, ax = plt.subplots(figsize=(5.4, 3.8))
    im = ax.imshow(M, cmap="viridis_r", aspect="auto")
    ax.set_xticks(range(len(etas)), [str(e) for e in etas])
    ax.set_yticks(range(len(T0s)), [str(t) for t in T0s])
    ax.set_xlabel("eta (enfriamiento)")
    ax.set_ylabel("T0 (km)")
    ax.set_title("SA: costo medio (km) segun parametros")
    for a_ in range(len(T0s)):
        for b_ in range(len(etas)):
            ax.text(b_, a_, f"{M[a_, b_]:,.0f}", ha="center", va="center",
                    color=("white" if M[a_, b_] > M.min() + 0.5 * (M.max() - M.min()) else "black"), fontsize=8)
    fig.colorbar(im, ax=ax, label="km")
    fig.tight_layout()
    fig.savefig("figuras/sensibilidad.png", dpi=170)
    plt.close(fig)

    # 5.6 Animaciones: ruta en movimiento y evolución del costo
    generar_animaciones()

    print(json.dumps({k: resumen[k] for k in ("optimo_exacto_km", "hc", "sa", "costo_inicial_medio")},
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()