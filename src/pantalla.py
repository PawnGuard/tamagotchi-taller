# pantalla.py — la OLED SSD1306 de 128x64 pixeles, por I2C.
#
# Se dibuja en `fb` (un FrameBuffer, que vive en la RAM) y luego mostrar()
# manda los 1024 bytes a la pantalla de un jalon. Dibujar en RAM es rapido;
# mandar por I2C tarda ~14 ms, por eso se hace una sola vez por cuadro.
from machine import Pin, I2C
import framebuf
import config

ANCHO = 128
ALTO = 64
DIRECCION = 0x3C

buf = bytearray(ANCHO * ALTO // 8)
fb = framebuf.FrameBuffer(buf, ANCHO, ALTO, framebuf.MONO_VLSB)
_i2c = None


def _cmd(*cmds):
    for c in cmds:
        _i2c.writeto(DIRECCION, bytes((0x80, c)))


def iniciar():
    global _i2c
    _i2c = I2C(0, sda=Pin(config.PIN_SDA), scl=Pin(config.PIN_SCL), freq=config.OLED_FREQ)
    print("I2C:", [hex(d) for d in _i2c.scan()])
    girada = config.OLED_GIRADA
    _cmd(0xAE,                         # apagada mientras se configura
         0x20, 0x00,                   # direccionamiento horizontal
         0x40,                         # empieza en la linea 0
         0xA0 if girada else 0xA1,     # voltear de izquierda a derecha
         0xA8, ALTO - 1,               # 64 renglones
         0xC0 if girada else 0xC8,     # voltear de arriba a abajo
         0xD3, 0x00, 0xDA, 0x12,       # sin desfase; cableado de 128x64
         0xD5, 0x80, 0xD9, 0xF1, 0xDB, 0x30,
         0x81, 0xFF,                   # contraste al maximo
         0xA4, 0xA6,                   # mostrar la RAM, sin invertir
         0x8D, 0x14,                   # bomba de carga (genera el alto voltaje)
         0xAF)                         # encendida


def mostrar():
    _cmd(0x21, 0, ANCHO - 1, 0x22, 0, ALTO // 8 - 1)   # toda la pantalla
    _i2c.writeto(DIRECCION, b"\x40" + buf)
