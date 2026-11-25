# jugar.py — Pong contra la CPU. A sube la paleta, B la baja.
# Se sale con C, o manteniendo B apretado 5 segundos. Gana quien llegue a 5.
#
# Las posiciones son pixeles y las velocidades pixeles por segundo, asi la
# fisica no depende de cada cuanto se llame paso().
import botones
import sonido

NOMBRE = "JUGAR"

ANCHO, ALTO = 128, 64
ARRIBA = 10                  # la cancha empieza debajo del marcador
PALETA = 14                  # alto de las paletas
X_YO = 2                     # mi paleta, a la izquierda
X_CPU = ANCHO - 4            # la de la CPU, a la derecha
BOLA = 3
VEL_PALETA = 75
VEL_INICIAL = 55
VEL_MAXIMA = 150
ACELERA = 1.08               # cada golpe, la bola va 8% mas rapido
ESPERA_SAQUE = 800           # ms que la bola parpadea antes de salir
PUNTOS_PARA_GANAR = 5
SALIR_MS = 5000              # mantener B este tiempo = salir
COSTO_ENERGIA = 10
PREMIO_POR_PUNTO = 5         # felicidad por cada punto que le metes
PREMIO_GANAR = 10


class Pong:
    def __init__(self, nivel=50):
        # La CPU no es perfecta: su paleta tiene velocidad limitada.
        self.vel_cpu = 35 + 0.4 * nivel          # nivel 0..100 -> 35..75 px/s
        self.yo = self.cpu = 0                   # marcador
        self.y_yo = self.y_cpu = (ARRIBA + ALTO - PALETA) / 2
        self.saques = 0
        self.terminado = False
        self.sacar(hacia=-1)

    def sacar(self, hacia):
        """La bola al centro, quieta un momento, y luego sale hacia `hacia`."""
        self.bx = (ANCHO - BOLA) / 2
        self.by = (ARRIBA + ALTO - BOLA) / 2
        self.vel = VEL_INICIAL
        inclina = ((self.saques * 37) % 61 - 30) / 30    # un angulo distinto cada vez
        self.vx = hacia * self.vel
        self.vy = inclina * self.vel * 0.6
        self.saques += 1
        self.espera = ESPERA_SAQUE

    def paso(self, ms, arriba, abajo):
        if self.terminado:
            return
        s = ms / 1000
        tope = ALTO - PALETA
        # mi paleta
        if arriba:
            self.y_yo -= VEL_PALETA * s
        if abajo:
            self.y_yo += VEL_PALETA * s
        self.y_yo = max(ARRIBA, min(tope, self.y_yo))
        # la CPU sigue la bola si viene hacia ella; si no, regresa al centro
        if self.vx > 0 and self.bx > ANCHO / 3:
            meta = self.by + BOLA / 2 - PALETA / 2
        else:
            meta = (ARRIBA + tope) / 2
        mueve = self.vel_cpu * s
        self.y_cpu += max(-mueve, min(mueve, meta - self.y_cpu))
        self.y_cpu = max(ARRIBA, min(tope, self.y_cpu))

        if self.espera > 0:
            self.espera -= ms
            return
        self.bx += self.vx * s
        self.by += self.vy * s
        # rebota en el techo y en el piso
        if self.by < ARRIBA:
            self.by, self.vy = ARRIBA, abs(self.vy)
            sonido.tocar("tic")
        elif self.by > ALTO - BOLA:
            self.by, self.vy = ALTO - BOLA, -abs(self.vy)
            sonido.tocar("tic")
        # rebota en las paletas
        if self.vx < 0 and self.toca(X_YO, self.y_yo):
            self.golpe(self.y_yo, 1, X_YO + 2)
        elif self.vx > 0 and self.toca(X_CPU, self.y_cpu):
            self.golpe(self.y_cpu, -1, X_CPU - BOLA)
        # gol
        if self.bx + BOLA < 0:
            self.anotar(cpu=True)
        elif self.bx > ANCHO:
            self.anotar(cpu=False)

    def toca(self, x, y):
        return (self.bx < x + 2 and self.bx + BOLA > x
                and self.by < y + PALETA and self.by + BOLA > y)

    def golpe(self, y_paleta, hacia, x_bola):
        # Donde pega en la paleta decide el angulo: al centro sale recta, en las
        # orillas sale inclinada. Asi se puede apuntar.
        centro = y_paleta + PALETA / 2
        donde = (self.by + BOLA / 2 - centro) / (PALETA / 2)     # -1 .. 1
        donde = max(-1.0, min(1.0, donde))
        self.vel = min(VEL_MAXIMA, self.vel * ACELERA)
        self.vx = hacia * self.vel
        self.vy = donde * self.vel * 0.8
        self.bx = x_bola
        sonido.tocar("tic")

    def anotar(self, cpu):
        if cpu:
            self.cpu += 1
            sonido.tocar("perder")
        else:
            self.yo += 1
            sonido.tocar("ganar")
        if max(self.yo, self.cpu) >= PUNTOS_PARA_GANAR:
            self.terminado = True
        else:
            self.sacar(hacia=-1 if cpu else 1)   # saca hacia quien perdio el punto


# --- El apartado ---------------------------------------------------------------

partida = None
b_apretado = 0               # ms que lleva B apretado sin soltar


def empezar(bicho):
    global partida, b_apretado
    if bicho.energia < 15:
        return "CANSADO..."
    partida = Pong(nivel=bicho.felicidad)     # feliz juega mejor
    b_apretado = 0


def paso(bicho, ms):
    global b_apretado
    partida.paso(ms, "a" in botones.apretados, "b" in botones.apretados)
    b_apretado = b_apretado + ms if "b" in botones.apretados else 0
    return partida.terminado or b_apretado >= SALIR_MS


def tecla(bicho, t):
    return t == "c"


def terminar(bicho):
    p = partida
    bicho.felicidad += PREMIO_POR_PUNTO * p.yo
    if p.terminado and p.yo > p.cpu:
        bicho.felicidad += PREMIO_GANAR
    bicho.energia -= COSTO_ENERGIA
    bicho.hambre -= 5
    if p.terminado:
        return ("GANASTE %d-%d" if p.yo > p.cpu else "PERDISTE %d-%d") % (p.yo, p.cpu)


def dibujar(fb, bicho):
    p = partida
    fb.text("%d" % p.yo, 48, 0)
    fb.text("%d" % p.cpu, 72, 0)
    fb.hline(0, ARRIBA - 1, ANCHO, 1)
    for y in range(ARRIBA + 1, ALTO, 6):                 # la red punteada
        fb.vline(ANCHO // 2, y, 3, 1)
    fb.fill_rect(X_YO, int(p.y_yo), 2, PALETA, 1)
    fb.fill_rect(X_CPU, int(p.y_cpu), 2, PALETA, 1)
    if p.espera <= 0 or (p.espera // 150) % 2:          # parpadea antes del saque
        fb.fill_rect(int(p.bx), int(p.by), BOLA, BOLA, 1)
    if b_apretado > 1000:                                # barrita de "saliendo..."
        fb.rect(0, 1, 40, 6, 1)
        fb.fill_rect(1, 2, 38 * (b_apretado - 1000) // (SALIR_MS - 1000), 4, 1)
