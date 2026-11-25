# sin_nombre.py — EJERCICIO 2 del taller: este apartado es tuyo.
#
# Asi como esta: sale el bichito sonriendo y abajo tres puntos que se van
# llenando ( .  ..  ... ), como si estuviera pensando. C lo quita.
#
# Para empezar:
#   1. Ponle nombre (el menu lo muestra vacio):   NOMBRE = "PENSAR"
#   2. Decide que hace. Ideas:
#      - Que piense un numero al azar y tu lo adivines con A y B
#      - Que cuente cuantas veces apretaste A
#      - Que los puntos vayan mas rapido o mas lento (cambia PUNTOS_MS)
#      - Que al terminar de pensar diga algo con sonido.tocar(...)
import dibujo

NOMBRE = ""

PUNTOS_MS = 400                 # cada cuanto aparece un punto mas

tiempo = 0                      # ms que lleva abierto este apartado


def empezar(bicho):
    global tiempo
    tiempo = 0                  # no devuelve texto: se queda en pantalla


def paso(bicho, ms):
    global tiempo
    tiempo += ms


def tecla(bicho, t):
    return t == "c"


def dibujar(fb, bicho):
    dibujo.bichito(fb, bicho, "feliz")
    puntos = (tiempo // PUNTOS_MS) % 4          # 0, 1, 2, 3, 0, 1, 2, 3...
    for i in range(puntos):
        fb.fill_rect(54 + i * 8, 54, 4, 4, 1)  # cuadritos de 4x4 en fila
