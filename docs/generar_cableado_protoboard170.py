# Cableado en protoboard de 170 puntos — ESP32-C3 SuperMini + OLED 0.96" + 3 botones + piezo.
# Sin soldar (salvo la bateria). Genera cableado_protoboard170.png
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, FancyBboxPatch

P = 6.0                       # 0.1" en unidades del dibujo
COLS = 17
FILAS = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j"]
_pos = {}
y = 0
for f in FILAS:
    _pos[f] = y
    y += 3 * P if f == "e" else P     # canal central de 0.3"
MARGEN = 4.0
ALTO = _pos["j"] + 2 * MARGEN
ANCHO = (COLS - 1) * P + 2 * MARGEN
def X(c): return MARGEN + (c - 1) * P
def Y(f): return ALTO - MARGEN - _pos[f]

fig, ax = plt.subplots(figsize=(11, 9.5), dpi=180)
ax.set_aspect("equal"); ax.axis("off")

# --- protoboard ---
ax.add_patch(FancyBboxPatch((0, 0), ANCHO, ALTO, boxstyle="round,pad=0,rounding_size=2",
             fc="#F4F4F0", ec="#9A9A94", lw=1.2, zorder=0))
ax.add_patch(Rectangle((0, (Y("e") + Y("f")) / 2 - 1.2), ANCHO, 2.4, fc="#DADAD4", ec="none", zorder=0))
for c in range(1, COLS + 1):              # tiras internas (5 agujeros unidos por columna)
    for top, bot in (("a", "e"), ("f", "j")):
        ax.add_patch(FancyBboxPatch((X(c) - 1.5, Y(bot) - 1.5), 3, Y(top) - Y(bot) + 3,
                     boxstyle="round,pad=0,rounding_size=1.2", fc="#E3ECF7", ec="none", zorder=1))
for c in range(1, COLS + 1):
    for f in FILAS:
        ax.add_patch(Rectangle((X(c) - 0.6, Y(f) - 0.6), 1.2, 1.2, fc="#3C3C3C", ec="none", zorder=2))
for f in FILAS:
    ax.text(-1.5, Y(f), f, ha="right", va="center", fontsize=7, color="#333", family="monospace")
for c in range(1, COLS + 1):
    ax.text(X(c), ALTO + 1.0, str(c), ha="center", va="bottom", fontsize=7, color="#333", family="monospace")

# --- ESP32-C3 SuperMini: USB-C a la derecha, pines en filas c y g, columnas 10-17 ---
c0 = 10
xl, xr = X(c0) - 3.2, X(c0 + 7) + 3.2
ax.add_patch(FancyBboxPatch((xl, Y("g") - 3.3), xr - xl, Y("c") - Y("g") + 6.6,
             boxstyle="round,pad=0,rounding_size=1.5", fc="#1E1E1E", ec="#111", alpha=0.93, zorder=5))
ym = (Y("c") + Y("g")) / 2
ax.add_patch(Rectangle((xr - 2.5, ym - 4.5), 7.5, 9, fc="#9A9A9A", ec="#555", zorder=6))
ax.text(xr + 6.2, ym, "USB-C", rotation=90, ha="left", va="center", fontsize=6.5, color="#333")
ax.text((xl + xr) / 2, ym + 2.2, "ESP32-C3 SuperMini", ha="center", va="center", fontsize=7.5,
        color="white", weight="bold", zorder=7)
ax.text((xl + xr) / 2, ym - 2.2, "(componentes arriba)", ha="center", va="center", fontsize=5.5,
        color="#BBB", zorder=7)
arriba = ["G21", "G20", "G10", "G9", "G8", "G7", "G6", "G5"]   # fila c, col 10..17
abajo = ["G0", "G1", "G2", "G3", "G4", "3V3", "GND", "5V"]     # fila g, col 10..17
for i, (a, b) in enumerate(zip(arriba, abajo)):
    c = c0 + i
    for f, txt, dy in (("c", a, -2.4), ("g", b, 2.4)):
        ax.add_patch(Circle((X(c), Y(f)), 0.9, fc="#D4B24A", ec="#7A6220", zorder=7))
        ax.text(X(c), Y(f) + dy, txt, ha="center", va="center", fontsize=4.6, color="white",
                zorder=8, family="monospace")

# --- colores de nets ---
COL = {"GND": "#111111", "3V3": "#D62828", "G0": "#1B6FE0", "G1": "#2A9D4B", "G10": "#8E44AD",
       "SCL": "#F39C12", "SDA": "#00A8B5", "G7": "#8B5A2B"}

def punto(net, c, f):
    ax.add_patch(Circle((X(c), Y(f)), 0.9, fc=COL[net], ec="white", lw=0.6, zorder=10))

def puente(net, c1, f1, c2, f2, lw=2.6):
    ax.plot([X(c1), X(c2)], [Y(f1), Y(f2)], color=COL[net], lw=lw, solid_capstyle="round", zorder=9)
    punto(net, c1, f1); punto(net, c2, f2)

# --- botones a horcajadas del canal (patas en e y f) ---
# Las dos patas de la misma columna estan unidas por dentro: unen la tira de arriba
# con la de abajo. Al apretar se unen las dos columnas.
for nombre, c1, c2 in (("A", 1, 3), ("B", 4, 6), ("C", 7, 9)):
    cx = (X(c1) + X(c2)) / 2
    cy = (Y("e") + Y("f")) / 2
    ax.add_patch(FancyBboxPatch((cx - 7, cy - 7), 14, 14, boxstyle="round,pad=0,rounding_size=1",
                 fc="#2B2B2B", ec="#111", zorder=5))
    ax.add_patch(Circle((cx, cy), 3.6, fc="#555", ec="#222", zorder=6))
    ax.text(cx, cy, nombre, ha="center", va="center", fontsize=9, color="white", weight="bold", zorder=7)
    for c in (c1, c2):
        for f in ("e", "f"):
            ax.add_patch(Circle((X(c), Y(f)), 0.9, fc="#D4B24A", ec="#7A6220", zorder=7))

# --- cables (6, ninguno se cruza) ---
puente("G0", 10, "h", 3, "h")     # boton A: G0 -> columna 3
puente("G1", 11, "j", 6, "j")     # boton B: G1 -> columna 6
puente("G10", 12, "b", 9, "b")    # boton C: G10 -> columna 9
puente("GND", 16, "i", 7, "i")    # GND del C3 -> columna 7 (pata izquierda de C)
puente("GND", 7, "c", 4, "c")     # ... columna 4 (pata izquierda de B)
puente("GND", 4, "d", 1, "d")     # ... columna 1 (pata izquierda de A)

# --- OLED parada en la fila j, columnas 13-16, pantalla hacia ti ---
ox0, ox1 = (X(13) + X(16)) / 2 - 31.9, (X(13) + X(16)) / 2 + 31.9   # 27 mm de ancho
ax.add_patch(Rectangle((ox0, Y("j") - 4.6), ox1 - ox0, 3.4, fc="#1F3A5F", ec="#0D1F35", zorder=11))
ax.text((ox0 + ox1) / 2, Y("j") - 7.2, "OLED parada, con tira de pines a 90° (vista desde arriba)", ha="center", va="top",
        fontsize=5.5, color="#1F3A5F")
for c, net, txt in ((13, "SDA", "SDA"), (14, "SCL", "SCL"), (15, "3V3", "VCC"), (16, "GND", "GND")):
    punto(net, c, "j")
    ax.plot([X(c), X(c)], [Y("j"), Y("j") - 1.4], color=COL[net], lw=1.6, zorder=11)

# vista frontal de la OLED, debajo de la protoboard
fx, fy, fw, fh = ANCHO + 14, -46, 46, 46
ax.add_patch(FancyBboxPatch((fx, fy), fw, fh, boxstyle="round,pad=0,rounding_size=1.5",
             fc="#1F3A5F", ec="#0D1F35", zorder=3))
ax.add_patch(Rectangle((fx + 3, fy + 13), fw - 6, 28, fc="#04070B", ec="#5E7A96", zorder=4))
ax.text(fx + fw / 2, fy + 27, "HOLA\nBICHITO", ha="center", va="center", fontsize=8, color="#BFE9FF",
        zorder=5, family="monospace")
for i, (net, txt) in enumerate((("SDA", "SDA"), ("SCL", "SCL"), ("3V3", "VCC"), ("GND", "GND"))):
    px = fx + fw / 2 + (i - 1.5) * P
    ax.add_patch(Circle((px, fy + 4), 1.1, fc=COL[net], ec="#7A6220", zorder=5))
    ax.plot([px, px], [fy + 4, fy - 6], color="#B0B0B0", lw=1.6, zorder=2)
    ax.text(px, fy + 8, txt, ha="center", va="center", fontsize=4.6, color="white", family="monospace", zorder=5)
ax.text(fx + fw / 2, fy - 8, "OLED de frente, como la ves tú:\npines ABAJO (queda de cabeza;\n"
        "config.OLED_GIRADA = True la endereza)\nOJO: si tu módulo dice VCC GND en vez\n"
        "de GND VCC, NO sirve este truco", ha="center", va="top", fontsize=5.6, color="#333")

# --- piezo: G7 (col 15 arriba) y GND (col 7 arriba) ---
pz = (X(11), ALTO + 24)
ax.add_patch(Circle(pz, 9, fc="#2B2B2B", ec="#111", zorder=4))
ax.add_patch(Circle(pz, 2.2, fc="#C9A227", ec="#8A6A3A", zorder=5))
ax.text(pz[0] + 11, pz[1] + 4, "piezo 27-29 mm\n(cables con punta estañada\no pin macho)", ha="left",
        va="center", fontsize=6, color="#333")
ax.plot([pz[0] + 5, X(15)], [pz[1] - 7, Y("a")], color=COL["G7"], lw=2, zorder=9)
punto("G7", 15, "a")
ax.plot([pz[0] - 5, X(7)], [pz[1] - 7, Y("a")], color=COL["GND"], lw=2, zorder=9)
punto("GND", 7, "a")

# --- bateria ---
bx = xr + 14
ax.add_patch(Rectangle((bx, ym + 14), 9, 6, fc="#EEE", ec="#666", zorder=3))
ax.text(bx + 4.5, ym + 12, "JST-PH (batería)\ncables soldados a los\npads BAT+/BAT- de\nla cara inferior del C3",
        ha="center", va="top", fontsize=5.5, color="#333")
ax.plot([bx, xr - 4], [ym + 18, Y("c") + 3.3], color=COL["3V3"], lw=1.4, ls=(0, (3, 2)), zorder=4)
ax.plot([bx, xr - 7], [ym + 16, Y("c") + 3.3], color=COL["GND"], lw=1.4, ls=(0, (3, 2)), zorder=4)

# --- leyenda ---
ly = -22
items = [("GND", "GND"), ("3V3", "3.3 V"), ("G0", "G0 → botón A"), ("G1", "G1 → botón B"),
         ("G10", "G10 → botón C"), ("G7", "G7 → piezo"), ("SCL", "SCL = G4"), ("SDA", "SDA = G3")]
for i, (net, txt) in enumerate(items):
    col, row = i % 4, i // 4
    lx = col * 28
    lyy = ly - row * 4
    ax.plot([lx, lx + 4], [lyy, lyy], color=COL[net], lw=3)
    ax.text(lx + 5, lyy, txt, va="center", fontsize=6.5, color="#222")

ax.set_xlim(-6, ANCHO + 66); ax.set_ylim(fy - 40, ALTO + 38)
ax.set_title("Bichito — protoboard de 170 puntos  ·  ESP32-C3 SuperMini + OLED 0.96\"  (sin soldar)",
             fontsize=10, pad=6)
plt.tight_layout()
plt.savefig("cableado_protoboard170.png", bbox_inches="tight", facecolor="white")
print("ok")
