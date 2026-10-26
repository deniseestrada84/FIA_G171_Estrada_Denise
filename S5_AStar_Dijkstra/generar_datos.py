"""
Genera data/nodos.csv y data/aristas.csv para el caso de estudio:
red carretera simplificada entre cabeceras municipales de la region
Amecameca - Chalco - Oriente del Valle de Mexico (Estado de Mexico / CDMX).

IMPORTANTE (supuestos del modelo):
 - Las coordenadas son aproximadas (grados decimales) y sirven para el modelo academico.
 - El costo de cada arista (km) = distancia en linea recta (Haversine) x factor de sinuosidad.
   El factor (1.15 a 1.45) se fija con semilla para ser reproducible.
 - Como factor >= 1, el costo real de cada tramo NUNCA es menor que la linea recta,
   por lo que la heuristica Haversine es admisible y consistente.
 - Si se tienen distancias reales (p. ej. de Google Maps), basta reemplazar la columna
   'km' de data/aristas.csv; el resto del programa no cambia.
"""
import csv
import math
import random

NODOS = [
    # nombre, latitud, longitud
    ("Ecatzingo", 18.9556, -98.7447),
    ("Atlautla", 19.0231, -98.7875),
    ("Tepetlixpa", 19.0078, -98.8094),
    ("Ozumba", 19.0366, -98.7967),
    ("Juchitepec", 19.1022, -98.8697),
    ("Amecameca", 19.1253, -98.7658),
    ("Ayapango", 19.1197, -98.7497),
    ("Tenango del Aire", 19.1597, -98.8678),
    ("Tlalmanalco", 19.2025, -98.8008),
    ("Temamatla", 19.2000, -98.8667),
    ("Cocotitlan", 19.2333, -98.8667),
    ("Chalco", 19.2650, -98.8981),
    ("Ixtapaluca", 19.3167, -98.8833),
    ("Valle de Chalco", 19.2917, -98.9500),
    ("Tlahuac", 19.2667, -99.0000),
    ("Milpa Alta", 19.1917, -99.0236),
    ("Xochimilco", 19.2570, -99.1030),
    ("CDMX Centro", 19.4326, -99.1332),
]

ARISTAS = [
    ("Ecatzingo", "Atlautla"), ("Atlautla", "Ozumba"), ("Atlautla", "Tepetlixpa"),
    ("Tepetlixpa", "Ozumba"), ("Ozumba", "Amecameca"), ("Tepetlixpa", "Amecameca"),
    ("Ozumba", "Juchitepec"), ("Amecameca", "Ayapango"), ("Amecameca", "Tlalmanalco"),
    ("Amecameca", "Juchitepec"), ("Ayapango", "Tlalmanalco"), ("Ayapango", "Ecatzingo"),
    ("Juchitepec", "Tenango del Aire"), ("Tenango del Aire", "Temamatla"),
    ("Tlalmanalco", "Temamatla"), ("Tlalmanalco", "Cocotitlan"), ("Tlalmanalco", "Chalco"),
    ("Temamatla", "Cocotitlan"), ("Cocotitlan", "Chalco"), ("Chalco", "Ixtapaluca"),
    ("Chalco", "Valle de Chalco"), ("Ixtapaluca", "Valle de Chalco"),
    ("Valle de Chalco", "Tlahuac"), ("Tlahuac", "Milpa Alta"), ("Tlahuac", "Xochimilco"),
    ("Milpa Alta", "Xochimilco"), ("Xochimilco", "CDMX Centro"),
    ("Ixtapaluca", "CDMX Centro"), ("Tlahuac", "CDMX Centro"),
    ("Valle de Chalco", "CDMX Centro"),
]


def haversine(lat1, lon1, lat2, lon2):
    """Distancia en km entre dos puntos (formula de Haversine)."""
    r = 6371.0088
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


if __name__ == "__main__":
    random.seed(171)  # semilla fija = reproducible
    coord = {n: (la, lo) for n, la, lo in NODOS}
    with open("data/nodos.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["nombre", "lat", "lon"])
        w.writerows(NODOS)
    with open("data/aristas.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["origen", "destino", "km"])
        for a, b in ARISTAS:
            d = haversine(*coord[a], *coord[b])
            km = round(d * random.uniform(1.15, 1.45), 2)
            w.writerow([a, b, km])
    print(f"{len(NODOS)} nodos y {len(ARISTAS)} aristas escritos en data/")
