# sprites.py — los dibujos del bichito, hechos con texto.
#
#   '#' = pixel encendido    '.' = apagado
#
# Para dibujar uno nuevo: copia un bloque, cambia los '#' y respeta el ancho
# (todas las filas deben medir lo mismo). imagen() lo convierte en algo que
# se pega en la pantalla con fb.blit(imagen, x, y).
#
# El bichito es un FANTASMITA DE SABANA: un CUERPO que depende de su forma
# (bebe, bicho, angel, diablo, hacker) mas una CARA que depende de su animo.
import framebuf

# --- Cuerpos 15x16. La cara va en las columnas 5..9, renglones 3..7 ---------
CUERPOS = {
"bebe": """
...............
...............
......###......
....#######....
...#########...
...#########...
..###########..
..###########..
.#############.
..###########..
..###########..
..###########..
..##.##.##.##..
..#..#...#..#..
...............
...............
""",
# adulto comun: tuvo cuidados normales
"bicho": """
...............
.....#####.....
...#########...
..###########..
..###########..
.#############.
.#############.
.#############.
###############
.#############.
.#############.
.#############.
.#############.
.#############.
.##.###.###.##.
..#..#...#..#..
""",
# cuidados perfectos: aureola y alitas
"angel": """
...............
....#######....
...............
....#######....
...#########...
..###########..
#.###########.#
##.#########.##
##.#########.##
#.###########.#
..###########..
..###########..
..###########..
..###########..
..##.##.##.##..
..#..#...#..#..
""",
# descuidado: cuernitos y colita
"diablo": """
...............
..#.........#..
..##.......##..
..###########..
..###########..
.#############.
.#############.
.#############.
###############
.#############.
.#############.
.##############
.#############.
.#############.
.##.###.###.##.
..#..#...#..#..
""",
# forma secreta (buen cuidado y muchos duelos ganados): capucha
"hacker": """
...............
.....#####.....
...#########...
..####...####..
..###.....###..
.####.....####.
.####.....####.
.#####...#####.
###############
.#############.
.#############.
.#############.
.#############.
.#############.
.##.###.###.##.
..#..#...#..#..
""",
}

# --- Caras 5x5. Se pintan INVIRTIENDO pixeles: sobre la sabana hacen hoyos y
# dentro de la capucha del hacker se encienden. 'x' = invertir ----------------
CARAS = {
"normal": """
.....
.x.x.
.x.x.
.....
.....
""",
"parpadeo": """
.....
.....
xx.xx
.....
.....
""",
"feliz": """
.x.x.
.x.x.
.....
x...x
.xxx.
""",
"triste": """
.x.x.
.x.x.
.....
.xxx.
x...x
""",
"guino": """
.x...
.x.xx
.....
x...x
.xxx.
""",
"dormido": """
.....
.....
xx.xx
.....
..x..
""",
}

HUEVO = """
......###......
....#######....
...#########...
..####..#####..
..###....####..
.#####..######.
.#############.
.#############.
.#######..####.
.######....###.
.#######..####.
.#############.
..###########..
..###########..
...#########...
.....#####.....
"""

TUMBA = """
...............
.....#####.....
...#########...
..#####.#####..
..#####.#####..
..###.....###..
..#####.#####..
..#####.#####..
..#####.#####..
..###########..
..###########..
..###########..
..###########..
.#############.
###############
###############
"""

CACA = """
...#....
..##....
..###...
.####...
#######.
########
.######.
..####..
"""

# --- Manos para el duelo de piedra, papel o tijera (10x16) ------------------
MANOS = {
"piedra": """
..........
..........
..........
..........
...####...
..#.#.#.#.
.##.#.#.#.
.#########
.#########
.#.#######
.##.######
.#########
..#######.
...#####..
...#####..
..........
""",
"papel": """
....#.....
..#.#.#...
..#.#.#...
..#.#.#.#.
..#.#.#.#.
..#######.
#.#######.
##.######.
.#.######.
.########.
..#######.
..#######.
...#####..
...#####..
...#####..
..........
""",
"tijera": """
.#.....#..
.##...##..
..#...#...
..##.##...
...#.#....
...###....
..#####...
.#######..
.#.######.
.##.#####.
.#########
.########.
..#######.
...#####..
...#####..
..........
""",
"duda": """
..........
...####...
..######..
.###..###.
.##....##.
......###.
.....###..
....###...
....##....
....##....
..........
....##....
....##....
..........
..........
..........
""",
}


# --- De texto a imagen --------------------------------------------------------

def _filas(arte):
    return arte.strip("\n").split("\n")


_guardadas = {}


def imagen(arte, escala=1, cara=None):
    """Convierte el arte en un FrameBuffer listo para fb.blit().
    escala=2 lo dibuja al doble. cara= pinta esa cara encima (solo cuerpos).
    Cada imagen se calcula una sola vez y se guarda: llamarla en cada cuadro
    no cuesta nada."""
    clave = (arte, escala, cara)
    if clave not in _guardadas:
        _guardadas[clave] = _convertir(arte, escala, cara)
    return _guardadas[clave]


def _convertir(arte, escala, cara):
    filas = [list(f) for f in _filas(arte)]
    if cara:
        for y, fila in enumerate(_filas(CARAS[cara])):
            for x, c in enumerate(fila):
                if c == "x":
                    p = filas[3 + y][5 + x]
                    filas[3 + y][5 + x] = "." if p == "#" else "#"
    ancho, alto = len(filas[0]) * escala, len(filas) * escala
    fb = framebuf.FrameBuffer(bytearray(ancho * ((alto + 7) // 8)), ancho, alto, framebuf.MONO_VLSB)
    for y, fila in enumerate(filas):
        if len(fila) * escala != ancho:
            raise ValueError("la fila %d no mide lo mismo que las demas" % y)
        for x, c in enumerate(fila):
            if c == "#":
                fb.fill_rect(x * escala, y * escala, escala, escala, 1)
    return fb


def bichito(forma, cara, escala=1):
    """El fantasmita con esa forma y esa cara."""
    return imagen(CUERPOS[forma], escala, cara)
