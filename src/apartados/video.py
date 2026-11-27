# video.py — reproduce el video que hiciste con herramientas/video_a_oled.py.
#
#   A = pausa / sigue      B = desde el principio      C = salir
#
# EJERCICIO: ponle musica a tu video. Escribe tu melodia en MELODIA (abajo):
# es una lista de (nota, duracion). Suena al abrir el video y se repite sola.
#
# El video puede pesar cientos de KB: no cabe en la RAM. Por eso se lee de la
# flash UN cuadro a la vez (1024 bytes), justo cuando toca mostrarlo. Es lo
# mismo que hace un reproductor de video de verdad: leer, mostrar, olvidar.
import framebuf
import struct
import sonido

NOMBRE = "VIDEO"

# --- La musica -------------------------------------------------------------------
# Notas: el nombre y la octava. DO4 es el "do central" del piano. Cada octava
# hacia arriba es el doble de frecuencia (DO5 = 2 x DO4). _S = sostenido.
DO4, DO_S4, RE4, RE_S4, MI4, FA4, FA_S4, SOL4, SOL_S4, LA4, LA_S4, SI4 = (
    262, 277, 294, 311, 330, 349, 370, 392, 415, 440, 466, 494)
DO5, DO_S5, RE5, RE_S5, MI5, FA5, FA_S5, SOL5, SOL_S5, LA5, LA_S5, SI5 = (
    523, 554, 587, 622, 659, 698, 740, 784, 831, 880, 932, 988)
DO6 = 1047
_ = 0                           # silencio

# Duraciones: el BPM dice cuantas NEGRAS caben en un minuto.
BPM = 113                       # Rickroll original ~113 BPM
NEGRA = 60000 // BPM
BLANCA = NEGRA * 2
CORCHEA = NEGRA // 2
SEMICORCHEA = NEGRA // 4
NEGRA_PUNTILLO = int(NEGRA * 1.5)
CORCHEA_PUNTILLO = int(CORCHEA * 1.5)

# Melodia principal de "Never Gonna Give You Up" (Rick Astley - estribillo)
MELODIA = (
    # Frase 1 ("Never gonna give you up")
    (DO5, SEMICORCHEA), (RE5, SEMICORCHEA), (FA5, SEMICORCHEA), (RE5, SEMICORCHEA),
    (LA5, CORCHEA_PUNTILLO), (LA5, CORCHEA_PUNTILLO), (SOL5, NEGRA_PUNTILLO),

    # Frase 2 ("Never gonna let you down")
    (DO5, SEMICORCHEA), (RE5, SEMICORCHEA), (FA5, SEMICORCHEA), (RE5, SEMICORCHEA),
    (SOL5, CORCHEA_PUNTILLO), (SOL5, CORCHEA_PUNTILLO), (FA5, CORCHEA_PUNTILLO), (MI5, SEMICORCHEA), (RE5, CORCHEA),

    # Frase 3 ("Never gonna run around and desert you")
    (DO5, SEMICORCHEA), (RE5, SEMICORCHEA), (FA5, SEMICORCHEA), (RE5, SEMICORCHEA),
    (FA5, NEGRA), (SOL5, CORCHEA), (MI5, CORCHEA_PUNTILLO), (RE5, SEMICORCHEA), (DO5, CORCHEA),
    (DO5, CORCHEA), (SOL5, NEGRA), (FA5, BLANCA),

    # Frase 4 ("Never gonna make you cry")
    (DO5, SEMICORCHEA), (RE5, SEMICORCHEA), (FA5, SEMICORCHEA), (RE5, SEMICORCHEA),
    (LA5, CORCHEA_PUNTILLO), (LA5, CORCHEA_PUNTILLO), (SOL5, NEGRA_PUNTILLO),

    # Frase 5 ("Never gonna say goodbye")
    (DO5, SEMICORCHEA), (RE5, SEMICORCHEA), (FA5, SEMICORCHEA), (RE5, SEMICORCHEA),
    (DO6, NEGRA), (MI5, CORCHEA), (FA5, CORCHEA_PUNTILLO), (MI5, SEMICORCHEA), (RE5, CORCHEA),

    # Frase 6 ("Never gonna tell a lie and hurt you")
    (DO5, SEMICORCHEA), (RE5, SEMICORCHEA), (FA5, SEMICORCHEA), (RE5, SEMICORCHEA),
    (FA5, NEGRA), (SOL5, CORCHEA), (MI5, CORCHEA_PUNTILLO), (RE5, SEMICORCHEA), (DO5, CORCHEA),
    (DO5, CORCHEA), (SOL5, NEGRA), (FA5, BLANCA),
)

sonido.MELODIAS["video"] = MELODIA

# --- El video ----------------------------------------------------------------------
ARCHIVO = __file__.rsplit("/", 1)[0] + "/video_cuadros.bin"
ENCABEZADO = 9                  # "VID1" + fps + numero de cuadros + ancho + alto

archivo = None
fps = 10
total = 0
ancho = alto = 0
tiempo = 0                      # ms desde el principio (no avanza en pausa)
pausa = False
mostrado = -1                   # que cuadro esta cargado en `buf`
buf = None
cuadro = None


def empezar(bicho):
    global archivo, fps, total, ancho, alto, tiempo, pausa, mostrado, buf, cuadro
    try:
        archivo = open(ARCHIVO, "rb")
    except OSError:
        return "SIN VIDEO"      # todavia no has convertido ninguno
    cabeza = archivo.read(ENCABEZADO)
    if cabeza[:4] != b"VID1":
        archivo.close()
        return "VIDEO DANADO"
    fps, total, ancho, alto = struct.unpack("<BHBB", cabeza[4:])
    buf = bytearray(ancho * alto // 8)
    cuadro = framebuf.FrameBuffer(buf, ancho, alto, framebuf.MONO_VLSB)
    tiempo, pausa, mostrado = 0, False, -1
    sonido.tocar("video")


def paso(bicho, ms):
    global tiempo, mostrado
    if not pausa:
        tiempo += ms
        if not sonido.sonando():                # se acabo la melodia: otra vez
            sonido.tocar("video")
    n = (tiempo * fps // 1000) % total          # que cuadro toca (y da la vuelta)
    if n != mostrado:
        archivo.seek(ENCABEZADO + n * len(buf))
        archivo.readinto(buf)
        mostrado = n


def tecla(bicho, t):
    global pausa, tiempo
    if t == "a":
        pausa = not pausa
        if pausa:
            sonido.callar()
        else:
            sonido.tocar("video")               # al seguir, la musica empieza de nuevo
    elif t == "b":
        tiempo = 0
        sonido.tocar("video")
    return t == "c"


def terminar(bicho):
    sonido.callar()
    archivo.close()


def dibujar(fb, bicho):
    if mostrado >= 0:
        fb.blit(cuadro, 0, 0)
    if pausa:
        fb.fill_rect(118, 2, 3, 9, 1)           # simbolo de pausa
        fb.fill_rect(123, 2, 3, 9, 1)
