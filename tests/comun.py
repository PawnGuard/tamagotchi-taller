# comun.py — lo que comparten las pruebas. Cada prueba hace `import comun`
# ANTES de importar cualquier modulo del bichito.
#
#   python3 -m unittest discover -s tests -v
import os
import sys
import time

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, "stubs"))          # machine, framebuf falsos
sys.path.insert(0, os.path.join(AQUI, "..", "src"))

# MicroPython tiene relojes en milisegundos que CPython no tiene.
if not hasattr(time, "ticks_ms"):
    time.ticks_ms = lambda: int(time.monotonic() * 1000)
    time.ticks_diff = lambda a, b: a - b
    time.ticks_add = lambda a, b: a + b
    time.sleep_ms = lambda ms: time.sleep(ms / 1000)

import framebuf


class Pantalla(framebuf.FrameBuffer):
    """Un FrameBuffer de 128x64 que ademas anota que textos e imagenes se
    dibujaron, para que las pruebas puedan preguntar "salio Saludando?"."""

    def __init__(self):
        super().__init__(bytearray(1024), 128, 64, framebuf.MONO_VLSB)
        self.limpiar()

    def limpiar(self):
        self.textos = []
        self.imagenes = []
        self.rellenos = []

    def fill(self, c):
        self.limpiar()
        super().fill(c)

    def text(self, s, x, y, c=1):
        self.textos.append(str(s))
        super().text(s, x, y, c)

    def blit(self, img, x, y, key=-1, palette=None):
        self.imagenes.append(img)
        super().blit(img, x, y, key, palette)

    def fill_rect(self, x, y, w, h, c):
        self.rellenos.append((x, y, w, h))
        super().fill_rect(x, y, w, h, c)

    def todo(self):
        return " | ".join(self.textos)


class RadioFalsa:
    """Reemplaza a radio.py: lo que el bichito manda le llega a `rival` (un
    duelo.Duelo) y lo que el rival deja en su salida le llega al bichito."""

    def __init__(self, radio, rival=None):
        self.encendida = False
        self.rival = rival
        self.entrada = []
        radio.mi_id = lambda: "AAAA"
        radio.encender = self.encender
        radio.apagar = self.apagar
        radio.enviar = self.enviar
        radio.recibir = self.recibir

    def encender(self):
        self.encendida = True

    def apagar(self):
        self.encendida = False

    def enviar(self, datos):
        if self.rival:
            self.rival.recibir(datos)

    def recibir(self):
        if self.rival:
            self.entrada += self.rival.salida
            self.rival.salida = []
        return self.entrada.pop(0) if self.entrada else None
