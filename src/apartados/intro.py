# intro.py — la presentacion del Tamagotchi: "Hola!", guino y video.
#
#   1. "Hola!" en GRANDE: aparece creciendo y rebota.
#   2. El fantasmita al triple de tamano GUINA el ojo, con las barras H F E
#      arriba y la edad abajo, como en la pantalla normal.
#   3. Pasa al video intro_cuadros.bin y, cuando se acaba, vuelve al menu.
#
#   A = saltar a la siguiente parte    B = desde el principio    C = salir
#
# Para cambiar el video:
#   python3 herramientas/video_a_oled.py otro.mp4 --salida src/apartados/intro_cuadros.bin
# Para que salga solo al prender la placa: INTRO_AL_PRENDER = True en config.py.
import framebuf
import struct
import dibujo
import sonido
import sprites

NOMBRE = "INTRO"
SIEMPRE = True                  # sale aunque sea huevo o este dormido

SALUDO = "Hola!"                # maximo 5 letras: a escala 3 cada una mide 24 px
HOLA_MS = 2000                  # cuanto dura el "Hola!"
GRANDE = 3                      # el fantasmita al triple (en casa sale a x1 o x2)
GUINO_MS = 3000                 # cuanto dura el fantasmita
GUINA_DESDE, GUINA_HASTA = 900, 1500    # cuando cierra el ojo (dentro de su parte)

sonido.MELODIAS["hola"] = ((784, 80), (0, 30), (1047, 160))
sonido.MELODIAS["guino"] = ((1319, 50), (0, 30), (1568, 110))

ARCHIVO = __file__.rsplit("/", 1)[0] + "/intro_cuadros.bin"
ENCABEZADO = 9                  # "VID1" + fps + numero de cuadros + ancho + alto

HOLA, GUINO, VIDEO = "hola", "guino", "video"

tiempo = 0                      # ms desde que empezo la parte actual
parte = HOLA
guino_sono = False
archivo = None
fps = total = 0
buf = cuadro = None
mostrado = -1


def empezar(bicho):
    _ir(HOLA)


def _ir(nueva):
    """Cambia de parte y la prepara. Devuelve True si ya no hay que seguir."""
    global parte, tiempo, guino_sono
    parte, tiempo, guino_sono = nueva, 0, False
    if nueva == HOLA:
        sonido.tocar("hola")
    elif nueva == VIDEO:
        sonido.callar()
        return not _abrir_video()
    return False


def _abrir_video():
    global archivo, fps, total, buf, cuadro, mostrado
    _cerrar_video()
    try:
        archivo = open(ARCHIVO, "rb")
    except OSError:
        return False            # sin video: la intro termina en el guino
    cabeza = archivo.read(ENCABEZADO)
    if cabeza[:4] != b"VID1":
        _cerrar_video()
        return False
    fps, total, ancho, alto = struct.unpack("<BHBB", cabeza[4:])
    buf = bytearray(ancho * alto // 8)
    cuadro = framebuf.FrameBuffer(buf, ancho, alto, framebuf.MONO_VLSB)
    mostrado = -1
    return True


def _cerrar_video():
    global archivo
    if archivo:
        archivo.close()
        archivo = None


def paso(bicho, ms):
    global tiempo, mostrado, guino_sono
    tiempo += ms
    if parte == HOLA:
        if tiempo >= HOLA_MS:
            return _ir(GUINO)
    elif parte == GUINO:
        if tiempo >= GUINA_DESDE and not guino_sono:
            guino_sono = True
            sonido.tocar("guino")
        if tiempo >= GUINO_MS:
            return _ir(VIDEO)
    else:
        n = tiempo * fps // 1000                # que cuadro toca
        if n >= total:
            return True                         # se acabo el video: al menu
        if n != mostrado:
            archivo.seek(ENCABEZADO + n * len(buf))
            archivo.readinto(buf)
            mostrado = n


def tecla(bicho, t):
    if t == "a":                                # saltar a lo que sigue
        if parte == HOLA:
            return _ir(GUINO)
        if parte == GUINO:
            return _ir(VIDEO)
        return True
    if t == "b":
        _ir(HOLA)
    return t == "c"


def terminar(bicho):
    sonido.callar()
    _cerrar_video()


def posicion(forma):
    """Donde va el fantasmita para quedar centrado entre las barras (y=8) y
    la edad (y=54). Los cuerpos tienen renglones vacios arriba y abajo: se
    centra solo la parte dibujada."""
    filas = sprites.CUERPOS[forma].strip("\n").split("\n")
    llenas = [i for i, f in enumerate(filas) if "#" in f]
    alto = (llenas[-1] - llenas[0] + 1) * GRANDE
    x = (128 - len(filas[0]) * GRANDE) // 2
    y = 8 + (45 - alto) // 2 - llenas[0] * GRANDE
    return x, y


def guinando():
    return parte == GUINO and GUINA_DESDE <= tiempo < GUINA_HASTA


def dibujar(fb, bicho):
    if parte == HOLA:
        escala = 1 if tiempo < 100 else 2 if tiempo < 200 else 3   # aparece creciendo
        rebote = (tiempo // 250) % 2 if tiempo >= 300 else 0      # y luego rebota
        ancho, alto = 8 * len(SALUDO) * escala, 8 * escala
        fb.blit(dibujo.letrero(SALUDO, escala), (128 - ancho) // 2, (64 - alto) // 2 - rebote * 2)
    elif parte == GUINO:
        dibujo.barras(fb, bicho)
        forma = bicho.figura()
        if forma not in sprites.CUERPOS:        # huevo o tumba: sale el bebe
            forma = "bebe"
        cara = "guino" if guinando() else "feliz"
        flota = (tiempo // 300) % 2                 # sube y baja un pixel
        x, y = posicion(forma)
        fb.blit(sprites.bichito(forma, cara, GRANDE), x, y + flota)
        dibujo.centrado(fb, dibujo.edad(bicho), 54)
    elif mostrado >= 0:
        fb.blit(cuadro, 0, 0)
