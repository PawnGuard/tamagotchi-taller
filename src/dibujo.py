# dibujo.py — ayudas para dibujar en la pantalla de 128x64.
#
# La pantalla es un FrameBuffer `fb`. Lo basico de MicroPython:
#   fb.fill(0)                    borrar todo
#   fb.text("HOLA", x, y)         texto (cada letra mide 8x8 pixeles)
#   fb.pixel(x, y, 1)             un pixel
#   fb.rect(x, y, ancho, alto, 1) rectangulo (fill_rect: relleno)
#   fb.blit(imagen, x, y)         pegar un sprite
# Las coordenadas empiezan en la esquina de arriba a la izquierda (0, 0).
#
# Aqui hay atajos para lo que se repite: texto centrado, barras, el bichito
# y la pantalla de casa completa.
import sprites
from bicho import HUEVO, ADULTO, MUERTO

ANCHO = 128
CUADRO_MS = 450        # cada cuanto cambia la animacion (flotar, parpadear)

reloj = 0              # milisegundos desde que arranco (juego.py lo avanza)


def cuadro():
    """Un contador que sube cada CUADRO_MS: sirve para animar."""
    return reloj // CUADRO_MS


def centrado(fb, texto, y):
    fb.text(texto, (ANCHO - 8 * len(texto)) // 2, y)


def barra(fb, x, y, ancho, porcentaje):
    fb.rect(x, y, ancho, 6, 1)
    lleno = int((ancho - 2) * porcentaje / 100)
    if lleno > 0:
        fb.fill_rect(x + 1, y + 1, lleno, 4, 1)


def bichito(fb, bicho, cara=None, x=None, y=None):
    """Dibuja al bichito. Si no dices cara, pone la de su animo.
    Sin x ni y queda centrado. De adulto se dibuja al doble de tamano."""
    n = cuadro()
    figura = bicho.figura()
    escala = 2 if bicho.etapa == ADULTO else 1
    if x is None:
        x = (ANCHO - 15 * escala) // 2
    if y is None:
        y = 14 if escala == 2 else 24
    if figura == HUEVO:
        fb.blit(sprites.imagen(sprites.HUEVO), x + n % 2, y)      # se tambalea
        return
    if figura == MUERTO:
        fb.blit(sprites.imagen(sprites.TUMBA), x, y)
        return
    if cara is None:
        cara = bicho.animo()
        if cara == "normal" and n % 7 == 6:
            cara = "parpadeo"                                     # parpadea a ratos
    flota = n % 2 and cara in ("normal", "feliz")                 # sube y baja
    fb.blit(sprites.bichito(figura, cara, escala), x, y - (escala if flota else 0))


def casa(fb, bicho, abajo=None, recuadro=False):
    """La pantalla normal: barras arriba, el bichito y un texto abajo."""
    if bicho.etapa == MUERTO:
        centrado(fb, "R.I.P.", 4)
        bichito(fb, bicho)
        centrado(fb, abajo or "B: otro huevo", 54)
        return
    barras(fb, bicho)
    bichito(fb, bicho)
    if bicho.dormido():
        fb.text("Zz", 84, 16)
    if bicho.pide_atencion():
        fb.text("!", 36, 16)
    for i in range(bicho.caca):
        fb.blit(sprites.imagen(sprites.CACA), 100 + i * 9, 44)
    if recuadro:
        fb.rect(0, 52, ANCHO, 12, 1)
    centrado(fb, edad(bicho) if abajo is None else abajo, 54)


def barras(fb, bicho):
    """Las tres barras de arriba: Hambre, Felicidad y Energia."""
    fb.text("H", 0, 0)
    barra(fb, 9, 1, 30, bicho.hambre)
    fb.text("F", 44, 0)
    barra(fb, 53, 1, 30, bicho.felicidad)
    fb.text("E", 88, 0)
    barra(fb, 97, 1, 30, bicho.energia)


def edad(bicho):
    return "edad %dd %dh" % (int(bicho.edad // 1440), int(bicho.edad // 60) % 24)


_letreros = {}


def letrero(texto, escala):
    """Un texto en GRANDE: cada pixel de la letra se vuelve un cuadrito de
    escala x escala. Devuelve una imagen para fb.blit() (se calcula una vez)."""
    clave = (texto, escala)
    if clave not in _letreros:
        import framebuf
        ancho = 8 * len(texto)
        chico = framebuf.FrameBuffer(bytearray(ancho), ancho, 8, framebuf.MONO_VLSB)
        chico.text(texto, 0, 0, 1)
        e = escala
        grande = framebuf.FrameBuffer(bytearray(ancho * e * e), ancho * e, 8 * e, framebuf.MONO_VLSB)
        for y in range(8):
            for x in range(ancho):
                if chico.pixel(x, y):
                    grande.fill_rect(x * e, y * e, e, e, 1)
        _letreros[clave] = grande
    return _letreros[clave]
