# Stub de framebuf para correr la logica del juego en CPython (sin placa).
# Implementa solo lo que usa el juego, en formato MONO_VLSB, igual que el real.
MONO_VLSB = 0
MONO_HLSB = 3


class FrameBuffer:
    def __init__(self, buf, ancho, alto, formato):
        assert formato == MONO_VLSB, "el stub solo implementa MONO_VLSB"
        assert len(buf) >= ancho * ((alto + 7) // 8), "buffer chico"
        self.buf, self.ancho, self.alto = buf, ancho, alto

    def pixel(self, x, y, c=None):
        if not (0 <= x < self.ancho and 0 <= y < self.alto):
            return 0
        i, bit = (y >> 3) * self.ancho + x, 1 << (y & 7)
        if c is None:
            return 1 if self.buf[i] & bit else 0
        self.buf[i] = (self.buf[i] | bit) if c else (self.buf[i] & ~bit)

    def fill(self, c):
        for i in range(len(self.buf)):
            self.buf[i] = 0xFF if c else 0

    def fill_rect(self, x, y, w, h, c):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.pixel(xx, yy, c)

    def rect(self, x, y, w, h, c, f=False):
        if f:
            return self.fill_rect(x, y, w, h, c)
        self.hline(x, y, w, c); self.hline(x, y + h - 1, w, c)
        self.vline(x, y, h, c); self.vline(x + w - 1, y, h, c)

    def hline(self, x, y, w, c):
        self.fill_rect(x, y, w, 1, c)

    def vline(self, x, y, h, c):
        self.fill_rect(x, y, 1, h, c)

    def text(self, s, x, y, c=1):
        # sin fuente en el stub: marca un bloque 8x8 por caracter para que
        # las pruebas puedan comprobar "se dibujo algo aqui"
        for i, ch in enumerate(str(s)):
            if ch != " ":
                self.fill_rect(x + i * 8 + 1, y + 1, 6, 6, c)

    def blit(self, fb, x, y, key=-1, palette=None):
        for yy in range(fb.alto):
            for xx in range(fb.ancho):
                v = fb.pixel(xx, yy)
                if v != key:
                    self.pixel(x + xx, y + yy, v)
